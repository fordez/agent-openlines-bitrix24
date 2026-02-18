import os
import json
import firebase_admin
from firebase_admin import credentials, firestore
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
        
        self._db = firestore.client()
        self._redis = None

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        if cls._instance._redis is None:
            cls._instance._redis = await get_redis()
        return cls._instance

    def _get_cache_key(self, tenant_id: str) -> str:
        return f"config:tenant:{tenant_id}"

    async def get_tenant_config(self, tenant_id: str) -> dict:
        """
        Obtiene la configuración completa de un tenant.
        Busca en Redis primero, luego unifica datos de Firestore:
        1. installations/{tenant_id} -> para obtener el DOMINIO
        2. config-app/{tenant_id} -> UI settings
        3. config-architect/{tenant_id} -> Personality
        4. config-ai/{tenant_id} -> Tenant AI Settings
        5. config-secrets/{domain} -> Bitrix Secrets (Shared by domain)
        6. agents/{agent_id} -> (Legacy support, maybe optional now)
        """
        cache_key = self._get_cache_key(tenant_id)
        cached = await self._redis.get(cache_key)
        
        if cached:
            return json.loads(cached)

        print(f"📡 [Firestore] Cargando configuración completa para {tenant_id}...")
        
        # 1. Obtener Domain de Installation (CRÍTICO para secrets)
        install_doc = self._db.collection(Collections.INSTALLATIONS).doc(tenant_id).get()
        if not install_doc.exists:
            print(f"⚠️ Installation no encontrada para {tenant_id}")
            return None
            
        install_data = install_doc.to_dict()
        domain = install_data.get('domain')
        
        # Iniciar diccionarios
        app_data = {}
        architect_data = {}
        ai_data = {}
        secrets_data = {}
        
        # 2. Config App
        app_doc = self._db.collection(Collections.CONFIG_APP).doc(tenant_id).get()
        if app_doc.exists:
            app_data = app_doc.to_dict()

        # 3. Config Architect
        arch_doc = self._db.collection(Collections.CONFIG_ARCHITECT).doc(tenant_id).get()
        if arch_doc.exists:
            architect_data = arch_doc.to_dict()
            # Opcional: Cargar config de AI del arquitecto si fuera necesario
            # arch_ai = self._db.collection('config-architect').doc(tenant_id).collection('ai').doc('config').get()

        # 4. Config AI
        ai_doc = self._db.collection(Collections.CONFIG_AI).doc(tenant_id).get()
        if ai_doc.exists:
            ai_data = ai_doc.to_dict()

        # 5. Config Secrets (Por DOMINIO)
        if domain:
            secrets_doc = self._db.collection(Collections.CONFIG_SECRETS).doc(domain).get()
            if secrets_doc.exists:
                secrets_data = secrets_doc.to_dict()

        # 6. Active Agent Config (Dynamic from 'agents' collection)
        # Buscar el primer agente activo para este tenant
        agent_data = {}
        try:
            agents_ref = self._db.collection(Collections.AGENTS)
            query = agents_ref.where("tenantId", "==", tenant_id).where("isActive", "==", True).limit(1)
            docs = query.stream()
            for doc in docs:
                agent_payload = doc.to_dict()
                # Mapear campos del esquema AIAgent a la estructura plana de config
                agent_data = {
                    "role": agent_payload.get("role"),
                    "objective": agent_payload.get("objective"),
                    "tone": agent_payload.get("tone"),
                    "knowledge": agent_payload.get("knowledge"),
                    # Nuevos campos avanzados (types.ts synced)
                    "systemPrompt": agent_payload.get("systemPrompt"),
                    "model": agent_payload.get("model"),
                    "temperature": agent_payload.get("temperature"),
                    "provider": agent_payload.get("provider"),
                }
                print(f"🤖 [Firestore] Agente activo encontrado: {agent_payload.get('name')} ({doc.id})")
                break
        except Exception as e:
            print(f"⚠️ Error buscando agente activo: {e}")
        
        # Combinar todo (Prioridad: secrets > agent > ai > architect > app)
        # Flattened config for easier usage
        full_config = {
            "domain": domain,
            **app_data,
            **architect_data,
            **ai_data,
            **agent_data,  # Agent overrides AI/Architect defaults
            **secrets_data
        }
        
        # Guardar en Redis
        await self._redis.set(cache_key, json.dumps(full_config), ex=3600)
        print(f"✅ Config cached for {tenant_id} (Domain: {domain})")
        
        return full_config

    def start_listener(self):
        """
        Inicia listeners en tiempo real para mantener el caché sincronizado.
        """
        def on_agent_change(col_snapshot, changes, read_time):
            # No usado actualmente si migramos a config-architect, pero lo mantenemos por compatibilidad
            for doc in col_snapshot:
                 # asumiendo que el doc id es member_id o tiene campo tenantId
                 # Si doc.id es member_id:
                 self._update_cache_background(doc.id)

        def on_config_change(col_snapshot, changes, read_time):
            # Genérico para config-app, config-architect, config-ai donde doc.id == member_id
            for doc in col_snapshot:
                self._update_cache_background(doc.id)

        def on_secrets_change(doc_snapshot, changes, read_time):
            # Para config-secrets, el doc ID es el DOMINIO.
            # Debemos buscar qué tenants (member_ids) usan este dominio.
            for doc in doc_snapshot:
                domain = doc.id
                print(f"♻️ [Firestore] Secretos cambiaron para dominio {domain}. Buscando tenants afectados...")
                try:
                    # Buscar en installations quien tiene este domain
                    inst_docs = self._db.collection(Collections.INSTALLATIONS).where('domain', '==', domain).stream()
                    for inst in inst_docs:
                        member_id = inst.id
                        self._update_cache_background(member_id)
                except Exception as e:
                    print(f"❌ Error buscando tenants para dominio {domain}: {e}")

        # Listeners
        # 1. config-app
        self._db.collection(Collections.CONFIG_APP).on_snapshot(on_config_change)
        # 2. config-architect
        self._db.collection(Collections.CONFIG_ARCHITECT).on_snapshot(on_config_change)
        # 3. config-ai
        self._db.collection(Collections.CONFIG_AI).on_snapshot(on_config_change)
        # 4. config-secrets (propaga por domain)
        self._db.collection(Collections.CONFIG_SECRETS).on_snapshot(on_secrets_change)
        
        print("👀 [Firestore] Listeners activos para all config collections.")

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
