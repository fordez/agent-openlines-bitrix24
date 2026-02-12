"""
Gestión de sesiones de agente con locks distribuidos via Redis.
Las sesiones de agente se mantienen en RAM (no serializables),
pero los locks y metadata usan Redis para soporte multi-instancia.
"""
import os
import time
import asyncio
from dataclasses import dataclass, field
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from app.context import app, MCP_SERVER_NAME, TRAVEL_SERVER_NAME
from app.prompts import SYSTEM_PROMPT
from app.memory import format_history_str
from app.redis_client import get_redis

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
                except Exception:
                    pass
                print(f"  🧹 Sesión expirada limpiada para chat {cid}")


async def create_new_session(chat_id: str) -> AgentSession:
    """Crea una nueva sesión de agente para un chat_id."""
    # Cargar configuración desde el archivo Python (Fuente de Verdad)
    try:
        from agent_config import CONFIG
        config = CONFIG
    except ImportError:
        config = {}

    ai_config = config.get("ai", {})
    llm_provider = ai_config.get("provider", os.getenv("LLM_PROVIDER", "google")).lower()

    
    # Nota: El mcp-agent lee el modelo de mcp_agent.config.yaml, 
    # pero aquí podemos forzar la lógica de proveedor.

    history_seed = await format_history_str(chat_id)
    instruction = SYSTEM_PROMPT
    if history_seed:
        instruction = f"{SYSTEM_PROMPT}\n\n{history_seed}"

    agent_app = await app.run().__aenter__()

    travel_agent = Agent(
        name=f"travel_assistant_{chat_id}",
        instruction=instruction,
        server_names=[MCP_SERVER_NAME, TRAVEL_SERVER_NAME],
    )

    await travel_agent.__aenter__()

    if llm_provider == "openai":
        llm = await travel_agent.attach_llm(OpenAIAugmentedLLM)
    else:
        llm = await travel_agent.attach_llm(GoogleAugmentedLLM)

    session = AgentSession(
        agent=travel_agent,
        llm=llm,
        agent_app=agent_app,
    )

    print(f"  🆕 Nueva sesión creada para chat {chat_id} (provider: {llm_provider}, source: agent_config.json)")
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
