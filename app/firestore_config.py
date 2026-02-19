import os
import json
import asyncio
import sys
import firebase_admin

# Redirect all prints to stderr to avoid breaking MCP protocol
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)
from firebase_admin import credentials, firestore
from google.cloud import firestore as google_firestore
from app.redis_client import get_redis
from app.db_schema import Collections

class FirestoreConfigService:
    _instance = None
    def __init__(self):
        if not firebase_admin._apps:
            # 1. Try Base64 Env Var (Fly.io / Production)
            import base64
            encoded_key = os.getenv("FIRESTORE_KEY_CONTENT")
            
            if encoded_key:
                try:
                    import tempfile
                    # Decode base64 -> JSON string
                    decoded_json = base64.b64decode(encoded_key).decode('utf-8')
                    
                    # Write to a temporary file so Google Auth can read it (works for SA Key AND User ADC)
                    # We use delete=False to keep it available for the process life
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp:
                        temp.write(decoded_json)
                        temp_path = temp.name
                    
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_path
                    firebase_admin.initialize_app()
                    print(f"🔐 [Firestore] Initialized using content from FIRESTORE_KEY_CONTENT")
                except Exception as e:
                    print(f"❌ Error initializing via FIRESTORE_KEY_CONTENT: {e}")
                    pass
            
            # 2. Try Standard File detection (Local Dev or if GOOGLE_APPLICATION_CREDENTIALS already set)
            elif not firebase_admin._apps:
                # If env var is already set by user (e.g. local dev), initialize_app picks it up automatically
                # or we verify the default file exists
                default_path = "firestore-key.json"
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                     firebase_admin.initialize_app()
                     print(f"🔐 [Firestore] Initialized using existing GOOGLE_APPLICATION_CREDENTIALS")
                elif os.path.exists(default_path):
                    cred = credentials.Certificate(default_path)
                    firebase_admin.initialize_app(cred)
                    print(f"🔐 [Firestore] Initialized using local file: {default_path}")
            
            # 3. Fallback (GCP Environment / Mock)
            if not firebase_admin._apps:
                print("⚠️ [Firestore] No explicit credentials found. Using default/anonymous.")
                firebase_admin.initialize_app()
        
        self._db = firestore.client() # Sync client for listeners
        
        # Initialize Async Client
        try:
             # This will use the same GOOGLE_APPLICATION_CREDENTIALS or default auth
             self._async_db = google_firestore.AsyncClient()
             print("✅ [Firestore] AsyncClient initialized successfully.")
        except Exception as e:
             print(f"❌ [Firestore] Failed to initialize AsyncClient: {e}")
             self._async_db = None

        self._redis = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        if cls._instance._redis is None:
            cls._instance._redis = await get_redis()
        return cls._instance

    def _get_cache_key(self, tenant_id: str, bot_id: str = None) -> str:
        if bot_id:
            return f"config:tenant:{tenant_id}:bot:{bot_id}"
        return f"config:tenant:{tenant_id}"

    async def get_tenant_config(self, tenant_id: str, bot_id: str = None) -> dict:
        """
        Obtiene la configuración completa de un tenant/bot.
        1. installations/{tenant_id} -> para obtener el DOMINIO
        2. settings/ai -> Global AI Config
        3. agents (query) -> Active Agent (filtrado por tenantId y opcionalmente botId)
        """
        if not self._async_db:
             print("❌ [Firestore] cannot get_tenant_config: AsyncClient not ready.")
             return {}

        cache_key = self._get_cache_key(tenant_id, bot_id)
        cached = await self._redis.get(cache_key)
        
        if cached:
            return json.loads(cached)

        print(f"📡 [Firestore] Cargando configuración completa para {tenant_id}...")
        
        domain = tenant_id

        # Definir corutinas para fetch en paralelo
        async def fetch_doc(collection, doc_id):
            try:
                # Use .document() instead of .doc()
                doc_ref = self._async_db.collection(collection).document(doc_id)
                doc = await doc_ref.get()
                return doc.to_dict() if doc.exists else {}
            except Exception as e:
                print(f"❌ Error fetching {collection}/{doc_id}: {e}")
                return {}

        async def fetch_agent():
            try:
                agents_ref = self._async_db.collection(Collections.AGENTS)
                query = agents_ref.where(filter=google_firestore.FieldFilter("tenantId", "==", tenant_id))\
                                  .where(filter=google_firestore.FieldFilter("isActive", "==", True))
                
                # Opcional: Filtrar por botId específico si lo tenemos
                if bot_id:
                     query = query.where(filter=google_firestore.FieldFilter("botId", "==", str(bot_id)))

                query = query.limit(1)
                
                async for doc in query.stream():
                     return doc.to_dict()
                
            except Exception as e:
                print(f"⚠️ Error buscando agente activo: {e}")
            return {}

        start_time = asyncio.get_event_loop().time()
        print(f"📡 [Firestore] Iniciando carga paralela de documentos para {tenant_id}...")
        
        results = await asyncio.gather(
            fetch_doc(Collections.INSTALLATIONS, domain),
            fetch_doc('settings', 'ai'),
            fetch_doc(Collections.CONFIG_SECRETS, domain),
            fetch_agent()
        )
        
        end_time = asyncio.get_event_loop().time()
        print(f"⏱️ [Firestore] Carga completada en {end_time - start_time:.3f}s")
        
        install_data, ai_data, secrets_data, agent_payload = results

        if not install_data:
             print(f"⚠️ Installation Data no encontrada en installations/{domain}")
        
        if not ai_data:
             print("⚠️ [Firestore] Global AI Settings (settings/ai) not found!")

        # Process Agent Data
        agent_data = {}
        if agent_payload:
            agent_data = {
                "role": agent_payload.get("role"),
                "systemPrompt": agent_payload.get("systemPrompt"),
                "model": agent_payload.get("model"),
                "temperature": agent_payload.get("temperature"),
                "provider": agent_payload.get("provider"),
                "openaiApiKey": agent_payload.get("openaiApiKey") or agent_payload.get("openai_api_key"),
                "googleApiKey": agent_payload.get("googleApiKey") or agent_payload.get("google_api_key"),
            }
            print(f"🤖 [Firestore] Agente activo encontrado: {agent_payload.get('name')}")

        # Combinar todo (Prioridad: secrets > agent > ai)
        # Eliminamos config_app y config_architect por optimización (no usados por el bot)
        full_config = {
            "domain": domain,
            **ai_data,
            **agent_data,
            **secrets_data
        }
        
        # Guardar en Redis
        await self._redis.set(cache_key, json.dumps(full_config), ex=3600)
        print(f"✅ Config cached for {tenant_id} (Domain: {domain})")
        
        return full_config

    def start_listener(self):
        """
        Inicia listeners en tiempo real en segundo plano.
        """
        try:
            # 1. config-secrets (propaga por domain)
            self._db.collection(Collections.CONFIG_SECRETS).on_snapshot(self._on_secrets_change)
            print("👀 [Firestore] Listeners activos (Optimized: config-secrets only).")
        except Exception as e:
            print(f"⚠️ No se pudieron activar los listeners de Firestore: {e}")

    def _on_secrets_change(self, doc_snapshot, changes, read_time):
        for doc in doc_snapshot:
            domain = doc.id
            print(f"♻️ [Firestore] Secretos cambiaron para dominio {domain}.")
            self._update_cache_background(domain)

    async def warmup(self):
        """Pre-carga datos globales para evitar lag en el primer mensaje."""
        try:
            await self.get_tenant_config("warmup_test")
            print("🔥 [Firestore] Warmup completado.")
        except:
             pass

    def _update_cache_background(self, tenant_id: str):
        """Dispara una actualización de caché fuera del hilo del listener."""
        import redis
        try:
            r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            # Forzamos borrado para que el siguiente request haga el fetch unificado
            r.delete(self._get_cache_key(tenant_id))
            print(f"🔄 [Redis] Caché invalidado para tenant: {tenant_id} por cambio en Firestore.")
        except Exception as e:
            print(f"❌ Error invalidando caché en background: {e}")

_service = None

async def get_firestore_config() -> FirestoreConfigService:
    global _service
    if _service is None:
        _service = await FirestoreConfigService.get_instance()
    return _service
