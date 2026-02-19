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
    return r.lock(f"lock:chat:{chat_id}", timeout=600, blocking_timeout=300)


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
    
    # --- CONFIGURACIÓN GLOBAL (Variables de Entorno / GitHub Secrets) ---
    from app.config import config as ai_config
    llm_provider = ai_config.LLM_PROVIDER
    global_model = ai_config.MODEL
    global_temp = ai_config.TEMPERATURE
    global_api_key = ai_config.API_KEY

    # Si no hay key en el entorno, intentamos el loader legacy por si acaso
    if not global_api_key:
        global_api_key = get_secret(llm_provider)

    # --- CONFIGURACIÓN ESPECÍFICA (Firestore) ---
    # Traemos el prompt y permitimos sobrescribir modelo/temp si el usuario lo desea en firestore
    fs_service = await get_firestore_config()
    from app.context_vars import member_id_var
    tenant_id = member_id_var.get() or os.getenv("BITRIX_MEMBER_ID")
    
    # Nuevo: Extraer bot_id para filtrar correctamente en Firestore (si hay múltiples bots por portal)
    bot_id = os.getenv("BITRIX_BOT_ID") 
    
    config = await fs_service.get_tenant_config(tenant_id, bot_id=bot_id) if tenant_id else None
    
    dynamic_prompt = ""
    # Configuración de IA fija en el código (vía app.config)
    ai_model = global_model
    ai_temp = global_temp
    
    # Determinar Prompt desde Firestore (único dato dinámico por cliente)
    if config:
        if config.get('systemPrompt'):
            dynamic_prompt = config.get('systemPrompt')
            print(f"📜 [Sessions] Usando System Prompt desde Firestore para {tenant_id}")
        elif config.get('role'):
            from app.base_prompt import BASE_SYSTEM_PROMPT
            role = config.get('role', 'Asistente Virtual')
            dynamic_prompt = f"{BASE_SYSTEM_PROMPT}\n\n# CONFIGURACIÓN ESPECÍFICA DEL AGENTE\nRol: {role}"
            print(f"🤖 [Sessions] Usando rol de Agente Activo para {tenant_id}")
    
    if not dynamic_prompt:
        from app.prompts import get_system_prompt
        dynamic_prompt = await get_system_prompt()
        print(f"⚠️ [Sessions] Usando prompt local/default para {tenant_id}")

    # --- ENSAMBLAJE ---
    history_seed = await format_history_str(chat_id)
    instruction = dynamic_prompt
    if history_seed:
        instruction = f"{dynamic_prompt}\n\n{history_seed}"

    bot_name = os.getenv("BOT_NAME", "travel_assistant")
    agent_version = os.getenv("AGENT_VERSION", "1.0.0")

    if tenant_id:
        os.environ["BITRIX_MEMBER_ID"] = tenant_id

    travel_agent = Agent(
        name=f"{bot_name}_v{agent_version}_{chat_id}",
        instruction=instruction,
        server_names=[], # Vaciamos para no buscar subprocesos
    )

    # NUEVO: Registrar herramientas locales (In-Process)
    from app.bitrix_tools import BITRIX_TOOLS
    for name, func in BITRIX_TOOLS.items():
        travel_agent.register_tool(func)
        print(f"🛠️ [Sessions] Tool registrada localmente: {name}")

    # Reusar el AgentApp global (ahora es inmediato)
    from app.context import get_agent_app
    agent_app = await get_agent_app()
    
    # El Agent sí debe entrar en su contexto para inicializarse
    await travel_agent.__aenter__()

    # Configuración de LLM
    api_key = global_api_key

    if api_key:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}"
        print(f"🔑 [Sessions] Usando API Key GLOBAL: {masked_key}")
        
        # Poner en environ por compatibilidad
        env_var_name = "OPENAI_API_KEY" if llm_provider == "openai" else "GOOGLE_API_KEY"
        os.environ[env_var_name] = api_key
        
        if llm_provider == "openai":
            import openai
            openai.api_key = api_key
            os.environ["OPENAI_DEFAULT_MODEL"] = ai_model

    else:
        print("❌ [Sessions] CRITICAL: No se encontró API Key GLOBAL!!")
    
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
