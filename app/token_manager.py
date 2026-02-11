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
    """Gestiona tokens OAuth con Redis como backend y refresh automático."""
    
    REDIS_KEY_ACCESS = "bitrix24:access_token"
    REDIS_KEY_REFRESH = "bitrix24:refresh_token"
    REDIS_KEY_EXPIRES = "bitrix24:expires_at"
    
    def __init__(self):
        self._redis = None
        self._http_client = None
        self._domain = os.getenv("BITRIX_DOMAIN")
        self._client_id = os.getenv("CLIENT_ID")
        self._client_secret = os.getenv("CLIENT_SECRET")
        
    async def _get_redis(self):
        """Obtiene cliente Redis (lazy init)."""
        if self._redis is None:
            from app.redis_client import get_redis
            self._redis = await get_redis()
        return self._redis
    
    async def _get_http(self):
        """Obtiene cliente HTTP (lazy init)."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30)
        return self._http_client

    def _get_val(self, val):
        """Decodifica valores de Redis si vienen como bytes."""
        if val is None: return None
        if isinstance(val, bytes):
            return val.decode("utf-8")
        return val
    
    async def initialize_from_env(self):
        """Carga tokens iniciales desde .env al Redis si no existen."""
        access_token = os.getenv("ACCESS_TOKEN")
        refresh_token = os.getenv("REFRESH_TOKEN")
        raw_expires = os.getenv("EXPIRES_IN", "3600")
        
        if access_token and refresh_token:
            redis = await self._get_redis()
            
            # Verificamos si ya hay algo en Redis para no sobreescribir si ya está sincronizado
            existing = await redis.get(self.REDIS_KEY_ACCESS)
            if existing and self._get_val(existing) == access_token:
                # Ya está sincronizado
                return

            await redis.set(self.REDIS_KEY_ACCESS, access_token)
            await redis.set(self.REDIS_KEY_REFRESH, refresh_token)
            
            # Manejar raw_expires como segundos o timestamp
            try:
                exp_val = int(raw_expires)
                if exp_val > 1000000000000: # Milisegundos timestamp
                    expires_at = exp_val / 1000
                elif exp_val > 1000000000: # Segundos timestamp
                    expires_at = exp_val
                else: # Segundos relativos
                    expires_at = datetime.now().timestamp() + exp_val
            except ValueError:
                expires_at = datetime.now().timestamp() + 3600
                
            await redis.set(self.REDIS_KEY_EXPIRES, str(int(expires_at)))
            sys.stderr.write(f"✅ Tokens inicializados desde .env (expira en timestamp {int(expires_at)})\n")
        else:
            sys.stderr.write("⚠️ Advertencia: No se encontraron tokens completos en .env\n")
    
    async def get_token(self) -> str:
        """Obtiene un access_token válido. Auto-refresca si expira."""
        redis = await self._get_redis()
        
        expires_at_str = self._get_val(await redis.get(self.REDIS_KEY_EXPIRES))
        
        if expires_at_str:
            expires_at = float(expires_at_str)
            now = datetime.now().timestamp()
            if now + 300 >= expires_at: # 5 min de margen
                sys.stderr.write("🔄 Token próximo a expirar o expirado, refrescando...\n")
                await self._refresh_token()
        
        access_token = self._get_val(await redis.get(self.REDIS_KEY_ACCESS))
        if access_token:
            return access_token
        
        # Último recurso: intentar refresh
        sys.stderr.write("⚠️ No hay token en Redis, intentando refresh manual...\n")
        await self._refresh_token()
        access_token = self._get_val(await redis.get(self.REDIS_KEY_ACCESS))
        if access_token:
            return access_token
            
        raise ValueError("FALLO CRÍTICO: No se pudo obtener access_token")
    
    async def force_refresh(self):
        """Fuerza la renovación del token sin importar la fecha de expiración."""
        sys.stderr.write("🚀 Forzando refresh de token...\n")
        return await self._refresh_token()

    async def _refresh_token(self):
        """Refresca el token vía OAuth2 y sincroniza Redis + .env."""
        redis = await self._get_redis()
        refresh_token = self._get_val(await redis.get(self.REDIS_KEY_REFRESH))
        
        if not refresh_token:
            # Fallback al .env si Redis falló
            refresh_token = os.getenv("REFRESH_TOKEN")
            
        if not refresh_token:
            raise ValueError("No hay REFRESH_TOKEN disponible para renovar")
        
        if not self._client_id or not self._client_secret:
            raise ValueError("Faltan CLIENT_ID o CLIENT_SECRET para refrescar")
        
        token_url = "https://oauth.bitrix.info/oauth/token/"
        params = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "client_secret": self._client_secret,
            "refresh_token": refresh_token,
        }
        
        try:
            http = await self._get_http()
            # Bitrix recomienda POST para refrescar
            response = await http.post(token_url, params=params)
            
            if response.status_code != 200:
                err_body = response.text
                sys.stderr.write(f"❌ Error OAuth Bitrix ({response.status_code}): {err_body}\n")
                raise ValueError(f"Error refrescando token: {err_body}")

            data = response.json()
            new_access = data["access_token"]
            new_refresh = data["refresh_token"]
            expires_in = int(data.get("expires_in", 3600))
            
            # Sincronizar Redis
            await redis.set(self.REDIS_KEY_ACCESS, new_access)
            await redis.set(self.REDIS_KEY_REFRESH, new_refresh)
            expires_at = datetime.now().timestamp() + expires_in
            await redis.set(self.REDIS_KEY_EXPIRES, str(int(expires_at)))
            
            # Sincronizar .env para persistencia total
            update_env_file("ACCESS_TOKEN", new_access)
            update_env_file("REFRESH_TOKEN", new_refresh)
            update_env_file("EXPIRES_IN", str(int(expires_at * 1000))) # Guardar como ms timestamp para consistencia
            
            sys.stderr.write("✅ Token refrescado y sincronizado en Redis + .env\n")
            return new_access
            
        except Exception as e:
            sys.stderr.write(f"❌ Excepción en refresh_token: {e}\n")
            raise

async def get_token_manager() -> TokenManager:
    """Singleton getter."""
    global _token_manager
    from app.token_manager import TokenManager as TM # Avoid circulars
    if globals().get("_token_manager") is None:
        globals()["_token_manager"] = TM()
        await globals()["_token_manager"].initialize_from_env()
    return globals()["_token_manager"]
