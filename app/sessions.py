import os
import time
import asyncio
from dataclasses import dataclass, field
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from app.context import app, MCP_SERVER_NAME
from app.prompts import SYSTEM_PROMPT
from app.memory import format_history_str

SESSION_TTL_SECONDS = 30 * 60  # 30 minutos

@dataclass
class AgentSession:
    """Sesión persistente de un agente para un chat_id."""
    agent: Agent
    llm: object  # AugmentedLLM (Google o OpenAI)
    agent_app: object  # MCPApp running context
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)

    def is_expired(self) -> bool:
        return (time.time() - self.last_used) > SESSION_TTL_SECONDS

    def touch(self):
        self.last_used = time.time()

# Cache en memoria: chat_id -> AgentSession
_sessions: dict[str, AgentSession] = {}

# Lock por chat_id para máxima concurrencia entre conversaciones
_chat_locks: dict[str, asyncio.Lock] = {}
_global_lock = asyncio.Lock()  # solo para crear/limpiar locks y sessions dict

async def get_chat_lock(chat_id: str) -> asyncio.Lock:
    """Obtiene o crea un lock individual para un chat_id."""
    async with _global_lock:
        if chat_id not in _chat_locks:
            _chat_locks[chat_id] = asyncio.Lock()
        return _chat_locks[chat_id]

async def cleanup_expired_sessions():
    """Limpia sesiones expiradas del cache."""
    async with _global_lock:
        expired = [cid for cid, s in _sessions.items() if s.is_expired()]
        for cid in expired:
            session = _sessions.pop(cid, None)
            _chat_locks.pop(cid, None)
            if session:
                try:
                    await session.agent.__aexit__(None, None, None)
                except Exception:
                    pass
                print(f"  🧹 Sesión expirada limpiada para chat {cid}")

async def create_new_session(chat_id: str) -> AgentSession:
    """Crea una nueva sesión de agente para un chat_id."""
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Obtener historial previo para semilla (si existe de sesiones anteriores)
    history_seed = await format_history_str(chat_id)
    instruction = SYSTEM_PROMPT
    if history_seed:
        instruction = f"{SYSTEM_PROMPT}\n\n{history_seed}"

    # Iniciar el contexto de MCPApp
    agent_app = await app.run().__aenter__()

    travel_agent = Agent(
        name=f"travel_assistant_{chat_id}",
        instruction=instruction,
        server_names=[MCP_SERVER_NAME],
    )

    # Iniciar el contexto del agente
    await travel_agent.__aenter__()

    # Adjuntar el LLM apropiado
    if llm_provider == "openai":
        llm = await travel_agent.attach_llm(OpenAIAugmentedLLM)
    else:
        llm = await travel_agent.attach_llm(GoogleAugmentedLLM)

    session = AgentSession(
        agent=travel_agent,
        llm=llm,
        agent_app=agent_app,
    )

    print(f"  🆕 Nueva sesión de agente creada para chat {chat_id} (provider: {llm_provider}, mcp: {MCP_SERVER_NAME})")
    return session

def get_session(chat_id: str) -> AgentSession:
    """Busca una sesión existente."""
    return _sessions.get(chat_id)

async def set_session(chat_id: str, session: AgentSession):
    """Guarda una sesión en el cache."""
    async with _global_lock:
        _sessions[chat_id] = session

async def remove_session(chat_id: str):
    """Elimina una sesión del cache."""
    async with _global_lock:
        return _sessions.pop(chat_id, None)
