"""
Gestión de sesiones de agente con locks distribuidos via Redis.
Las sesiones de agente se mantienen en RAM (no serializables),
pero los locks y metadata usan Redis para soporte multi-instancia.
"""
import os
import time
import asyncio
from dataclasses import dataclass, field
import sys

# Redirect all prints to stderr to avoid breaking MCP protocol
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)

from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from app.context import app, MCP_SERVER_NAME
from app.firestore_config import get_firestore_config
from app.memory import format_history_str, clear_chat_history
from app.redis_client import get_redis
from app.secrets_loader import get_secret

SESSION_TTL_SECONDS = 30 * 60  # 30 minutos


@dataclass
class AgentSession:
    """Sesión persistente de un agente para un chat_id."""
    agent: Agent
    llm: object
    agent_app: object
    app_context_manager: object  # Store the CM to prevent GC and allow proper close
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return (time.time() - self.last_used) > SESSION_TTL_SECONDS

    def touch(self):
        self.last_used = time.time()


# Cache en RAM: chat_id -> AgentSession (no serializable)
_sessions: dict[str, AgentSession] = {}
_global_lock = asyncio.Lock()


async def get_chat_lock(chat_id: str):
    """
    Retorna un lock distribuido de Redis para un chat_id.
    Compatible con `async with`.
    """
    r = await get_redis()
    return r.lock(f"lock:chat:{chat_id}", timeout=120, blocking_timeout=60)


async def cleanup_expired_sessions():
    """Limpia sesiones expiradas del cache."""
    async with _global_lock:
        expired = [cid for cid, s in _sessions.items() if s.is_expired()]
        for cid in expired:
            session = _sessions.pop(cid, None)
            if session:
                try:
                    await session.agent.__aexit__(None, None, None)
                    if session.app_context_manager:
                        await session.app_context_manager.__aexit__(None, None, None)
                    
                    # Limpiar Redis al terminar sesión (según requerimiento user)
                    await clear_chat_history(cid)
                except Exception as e:
                    print(f"  ⚠️ Error cerrando sesión {cid}: {e}")
                print(f"  🧹 Sesión expirada limpiada para chat {cid}")


async def create_new_session(chat_id: str) -> AgentSession:
    """Crea una nueva sesión de agente para un chat_id."""
    # IMPORTANTE: No borrar el historial al iniciar sesión. 
    # Cloud Run apaga instancias (instancias a cero) frecuentemente.
    # Queremos que el bot recuerde lo anterior al re-encenderse por un nuevo mensaje.
    # await clear_chat_history(chat_id) 
    
    # AI config ahora vive en .env
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

    
    # Nota: El mcp-agent lee el modelo de mcp_agent.config.yaml, 
    # pero aquí podemos forzar la lógica de proveedor.

    history_seed = await format_history_str(chat_id)
    


    # Nuevo: Cargar configuración desde Firestore (con caché en Redis)
    from app.prompts import _DEFAULT_SYSTEM_PROMPT
    
    fs_service = await get_firestore_config()
    # Obtenemos el member_id del context var (seteado en main.py) o fallback env
    from app.context_vars import member_id_var
    tenant_id = member_id_var.get() or os.getenv("BITRIX_MEMBER_ID")
    
    config = await fs_service.get_tenant_config(tenant_id) if tenant_id else None
    
    if config:
        # 1. Check for explicit 'systemPrompt' (from config-architect or custom agent field)
        # This allows the Dashboard to fully control the prompt (overriding the codebase default)
        if config.get('systemPrompt'):
            dynamic_prompt = config.get('systemPrompt')
            print(f"📜 [Sessions] Usando System Prompt raw desde Firestore para {tenant_id}")
            
            # Optional: Si también hay variables de agente activo, las anexamos?
            # Por ahora, asumimos que si hay systemPrompt, es AUTOSIFICIENTE O INCLUYE VARIABLES.
            # Pero para soportar "Knowledge" dinámico + "System Prompt" base modificado, podríamos interpolar.
            # Simple override is safer for now based on user request "todo hay".
            
        # 2. Else, build from Active Agent systemPrompt + role
        elif config.get('role'):
            role = config.get('role', 'Asistente Virtual')
            
            from app.base_prompt import BASE_SYSTEM_PROMPT
            dynamic_prompt = f"{BASE_SYSTEM_PROMPT}\n\n# CONFIGURACIÓN ESPECÍFICA DEL AGENTE\nRol: {role}"
            print(f"🤖 [Sessions] Usando configuración de Agente Activo para {tenant_id}")
            
        else:
            # Fallback to local base
            from app.prompts import _DEFAULT_SYSTEM_PROMPT
            dynamic_prompt = _DEFAULT_SYSTEM_PROMPT
            print(f"⚠️ [Sessions] Config encontrada pero sin prompt/agente. Usando default local.")

        ai_model = config.get('model', os.getenv("AI_MODEL", "gpt-4o"))
        ai_temp = float(config.get('temperature', os.getenv("AI_TEMPERATURE", "0.2")))
        print(f"🎨 [Sessions] Modelo aplicado: {ai_model}")
    else:
        from app.prompts import get_system_prompt
        dynamic_prompt = await get_system_prompt()
        ai_model = os.getenv("AI_MODEL", "gpt-4o")
        ai_temp = float(os.getenv("AI_TEMPERATURE", "0.2"))
        print(f"⚠️ [Sessions] No se encontró config para {tenant_id}, usando local.")
    
    instruction = dynamic_prompt
    if history_seed:
        instruction = f"{dynamic_prompt}\n\n{history_seed}"

    bot_name = os.getenv("BOT_NAME", "travel_assistant")
    agent_version = os.getenv("AGENT_VERSION", "1.0.0")

    # Propagar tenant_id (env var sigue siendo BITRIX_MEMBER_ID por compatibilidad) al entorno
    if tenant_id:
        os.environ["BITRIX_MEMBER_ID"] = tenant_id

    travel_agent = Agent(
        name=f"{bot_name}_v{agent_version}_{chat_id}",
        instruction=instruction,
        server_names=[MCP_SERVER_NAME],
    )

    app_cm = app.run()
    agent_app = await app_cm.__aenter__()
    await travel_agent.__aenter__()

    # Configurar modelo por defecto en variables de entorno para que MCP Agent lo tome
    if ai_model:
        os.environ["OPENAI_DEFAULT_MODEL"] = ai_model
        # os.environ["GOOGLE_DEFAULT_MODEL"] = ai_model # Google adapter might use different env var or specific kwarg

    
    # Pass model and temperature via partial to the factory
    from functools import partial
    
    # Resolver API Key
    api_key = None
    if config:
        if config.get("provider"):
            llm_provider = config.get("provider").lower()
            print(f"🔄 [Sessions] Provider cambiado por Agente: {llm_provider}")

        # 1. Prioridad: Firestore (tenent-specific override)
        if llm_provider == "openai" and config.get("openaiApiKey"):
            api_key = config.get("openaiApiKey")
        elif llm_provider == "google" and config.get("googleApiKey"):
            api_key = config.get("googleApiKey")
    
    # 2. Fallback: secrets_loader (Environment or secrets.yaml)
    if not api_key:
        print("⚠️ [Sessions] API Key no encontrada en config. Intentando secrets_loader...")
        api_key = get_secret(llm_provider)

    if api_key:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"🔑 [Sessions] API Key encontrada: {masked_key}")
        
        # Poner en environ como fallback para librerías que lo busquen directamente
        env_var_name = "OPENAI_API_KEY" if llm_provider == "openai" else "GOOGLE_API_KEY"
        os.environ[env_var_name] = api_key
        
        # FIX: Algunos wrappers de mcp-agent pueden usar client legacy de OpenAI
        # Forzar configuración global también por si acaso
        if llm_provider == "openai":
            import openai
            openai.api_key = api_key
            print("🔧 [Sessions] openai.api_key set globalmente.")

    else:
        print("❌ [Sessions] CRITICAL: No se encontró API Key para el proveedor!!")
    
    llm_kwargs = {
        "model": ai_model,
        "temperature": ai_temp,
        "api_key": api_key
    }
    
    print(f"🔌 [Sessions] Attaching LLM ({llm_provider}): {ai_model} (T={ai_temp})")

    if llm_provider == "openai":
        factory = partial(OpenAIAugmentedLLM, **llm_kwargs)
        llm = await travel_agent.attach_llm(llm_factory=factory)
    else:
        factory = partial(GoogleAugmentedLLM, **llm_kwargs)
        llm = await travel_agent.attach_llm(llm_factory=factory)

    session = AgentSession(
        agent=travel_agent,
        llm=llm,
        agent_app=agent_app,
        app_context_manager=app_cm,
    )

    print(f"  🆕 Nueva sesión creada para chat {chat_id} (provider: {llm_provider})")
    return session


def get_session(chat_id: str) -> AgentSession:
    """Busca una sesión existente en RAM."""
    return _sessions.get(chat_id)


async def set_session(chat_id: str, session: AgentSession):
    """Guarda una sesión en el cache RAM."""
    async with _global_lock:
        _sessions[chat_id] = session


async def remove_session(chat_id: str):
    """Elimina una sesión del cache RAM."""
    async with _global_lock:
        return _sessions.pop(chat_id, None)
