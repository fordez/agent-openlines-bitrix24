"""
Gestor centralizado de tokens OAuth de Bitrix24.
Fuente única de verdad para todos los tokens, con refresh automático.
Usa Redis para compartir estado entre procesos (main y mcp_server).
"""
import os
import sys
import httpx
import json
from datetime import datetime, timedelta
from app.auth import update_env_file

class TokenManager:
    """Gestiona tokens OAuth con Redis como backend y Firestore como fuente de verdad."""
    
    def __init__(self):
        self._redis = None
        self._http_client = None
    
    def _get_redis_key(self, member_id: str, suffix: str) -> str:
        return f"bitrix24:{member_id}:{suffix}"

    async def _get_redis(self):
        if self._redis is None:
            from app.redis_client import get_redis
            self._redis = await get_redis()
        return self._redis
    
    async def _get_http(self):
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30)
        return self._http_client

    def _get_val(self, val):
        if val is None: return None
        if isinstance(val, bytes):
            return val.decode("utf-8")
        return val

    async def get_member_id_from_chat(self, chat_id: int) -> str:
        """Busca el member_id asociado a un chat_id en Redis."""
        if not chat_id:
            return None
        redis = await self._get_redis()
        val = await redis.get(f"map:chat_to_member:{chat_id}")
        return self._get_val(val)

    async def get_member_id(self) -> str:
        """Obtiene el member_id del contexto actual."""
        from app.context_vars import member_id_var
        m_id = member_id_var.get()
        if not m_id:
            # Intentar fallback de entorno si existe (para depuración)
            m_id = os.getenv("BITRIX_MEMBER_ID")
        return m_id

    async def get_credentials(self, member_id: str):
        """Obtiene CLIENT_ID y CLIENT_SECRET para un tenant (vía su domain)."""
        # Priorizar variables de entorno si están definidas (para test o mono-tenant)
        client_id = os.getenv("CLIENT_ID")
        client_secret = os.getenv("CLIENT_SECRET")
        
        if client_id and client_secret:
            return client_id, client_secret

        # Buscar en Firestore: config-secrets/{domain}
        from app.firestore_config import get_firestore_config
        fs = await get_firestore_config()
        
        # El member_id YA ES EL DOMINIO en esta arquitectura
        domain = member_id
        
        if not fs._async_db:
            raise ValueError("Firestore AsyncClient not initialized")

        doc = await fs._async_db.collection('config-secrets').document(domain).get()
        
        if doc.exists:
            data = doc.to_dict()
            return data.get('clientId'), data.get('clientSecret')
            
        raise ValueError(f"No se encontraron credenciales para el dominio {domain} en config-secrets")

    async def get_token(self, member_id: str = None) -> str:
        """Obtiene un access_token válido para el tenant especificado o el actual."""
        if not member_id:
            member_id = await self.get_member_id()
        
        if not member_id:
            raise ValueError("No se pudo determinar el member_id para obtener el token")

        redis = await self._get_redis()
        
        # 1. Intentar Redis
        access = self._get_val(await redis.get(self._get_redis_key(member_id, "access_token")))
        expires_at_str = self._get_val(await redis.get(self._get_redis_key(member_id, "expires_at")))
        
        if access and expires_at_str:
            expires_at = float(expires_at_str)
            if datetime.now().timestamp() + 300 < expires_at:
                return access

        # 2. Si no hay en Redis o expirado, intentar Firestore
        tokens = await self._fetch_from_firestore(member_id)
        if tokens:
            # Guardar en Redis para próximas llamadas
            await self._sync_to_redis(member_id, tokens)
            
            # Verificar si el de Firestore también expiró
            if datetime.now().timestamp() + 300 < tokens['expires_at']:
                return tokens['access_token']

        # 3. Si todo falló o expiró, refrescar
        sys.stderr.write(f"🔄 Refrescando token para tenant {member_id}...\n")
        return await self._refresh_token(member_id)

    async def _fetch_from_firestore(self, domain: str) -> dict:
        """Busca tokens en 'installations/{domain}' directamente."""
        from app.firestore_config import get_firestore_config
        fs = await get_firestore_config()

        if not fs._async_db:
             print("❌ [TokenManager] AsyncClient not ready.")
             return None

        # 1. Fetch Installation Data by Domain directly
        # Ahora asumimos que 'member_id' (argumento) ES el dominio
        try:
            doc = await fs._async_db.collection('installations').document(domain).get()
            
            if doc.exists:
                data = doc.to_dict()
                if 'accessToken' in data and 'refreshToken' in data:
                    return {
                        'access_token': data['accessToken'],
                        'refresh_token': data['refreshToken'],
                        'expires_at': data.get('expiresAt', 0) / 1000 if data.get('expiresAt', 0) > 10000000000 else data.get('expiresAt', 0),
                        'domain': data.get('domain', domain)
                    }
            else:
                print(f"❌ [TokenManager] No se encontró instalación para el dominio: {domain}")
        except Exception as e:
            print(f"❌ [TokenManager] Error fetching from firestore: {e}")
            
        return None

    async def _sync_to_redis(self, member_id: str, tokens: dict):
        redis = await self._get_redis()
        await redis.set(self._get_redis_key(member_id, "access_token"), tokens['access_token'])
        await redis.set(self._get_redis_key(member_id, "refresh_token"), tokens['refresh_token'])
        await redis.set(self._get_redis_key(member_id, "expires_at"), str(int(tokens['expires_at'])))
        if tokens.get('domain'):
            await redis.set(self._get_redis_key(member_id, "domain"), tokens['domain'])

    async def force_refresh(self, member_id: str = None):
        if not member_id:
            member_id = await self.get_member_id()
        return await self._refresh_token(member_id)

    async def _refresh_token(self, member_id: str):
        redis = await self._get_redis()
        refresh_token = self._get_val(await redis.get(self._get_redis_key(member_id, "refresh_token")))
        
        if not refresh_token:
            tokens = await self._fetch_from_firestore(member_id)
            if tokens:
                refresh_token = tokens['refresh_token']
        
        if not refresh_token:
            raise ValueError(f"No hay REFRESH_TOKEN disponible para el tenant {member_id}")
        
        client_id, client_secret = await self.get_credentials(member_id)
        
        token_url = "https://oauth.bitrix.info/oauth/token/"
        params = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        }
        
        http = await self._get_http()
        response = await http.post(token_url, params=params)
        
        if response.status_code != 200:
            raise ValueError(f"Error refrescando token ({member_id}): {response.text}")

        data = response.json()
        new_tokens = {
            'access_token': data["access_token"],
            'refresh_token': data["refresh_token"],
            'expires_at': datetime.now().timestamp() + int(data.get("expires_in", 3600))
        }
        
        # Sincronizar Redis
        await self._sync_to_redis(member_id, new_tokens)
        
        # Sincronizar Firestore
        from app.firestore_config import get_firestore_config
        fs = await get_firestore_config()
        if fs._async_db:
            await fs._async_db.collection('installations').document(member_id).update({
                'accessToken': new_tokens['access_token'],
                'refreshToken': new_tokens['refresh_token'],
                'expiresAt': int(new_tokens['expires_at'] * 1000) # Dashboard suele usar ms
            })
        
        return new_tokens['access_token']
async def get_token_manager() -> TokenManager:
    global _token_manager
    if globals().get("_token_manager") is None:
        globals()["_token_manager"] = TokenManager()
    return globals()["_token_manager"]
