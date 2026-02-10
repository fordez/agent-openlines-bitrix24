"""
Módulo de agente AI usando mcp-agent con GoogleAugmentedLLM (Gemini).
Implementa sesiones persistentes por chat_id para mantener contexto multi-turno nativo.
"""
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
import os
import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
from app.memory import add_message, format_history_str

load_dotenv()
from tools.crm.resolve_identity import resolve_identity
from tools.crm.enrich_identity import enrich_identity
from tools.crm.qualify_lead import qualify_lead
from tools.deal.get_or_create_deal import get_or_create_deal
from tools.deal.update_deal_stage import update_deal_stage
from tools.deal.update_deal_fields import update_deal_fields
from tools.deal.add_deal_note import add_deal_note
from tools.deal.close_deal import close_deal
from tools.calendar.get_availability import get_availability
from tools.calendar.create_event import create_event
from tools.calendar.update_event import update_event
from tools.calendar.cancel_event import cancel_event
from tools.calendar.get_event import get_event
from tools.calendar.schedule_meeting import schedule_meeting
from tools.calendar.reschedule_event import reschedule_event
from tools.activity.create_activity import create_activity
from tools.activity.update_activity import update_activity
from tools.activity.complete_activity import complete_activity
from tools.activity.schedule_followup import schedule_followup
from tools.automation.detect_sales_stage import detect_sales_stage
from tools.automation.predict_close_probability import predict_close_probability
from tools.automation.handle_objection import handle_objection
from tools.automation.reactivate_lead import reactivate_lead

# Lista de funciones (tools) disponibles para el agente
AGENT_FUNCTIONS = [
    resolve_identity, enrich_identity, qualify_lead,
    get_or_create_deal, update_deal_stage, update_deal_fields,
    add_deal_note, close_deal,
    get_availability, create_event, update_event, reschedule_event,
    cancel_event, get_event, schedule_meeting,
    create_activity, update_activity, complete_activity, schedule_followup,
    detect_sales_stage, predict_close_probability, handle_objection, reactivate_lead
]

app = MCPApp(name="bot_viajes_agent")

SYSTEM_PROMPT = """Eres el Coordinador de Agendamiento Inteligente de 'Viajes y Viajes'.
TU ÚNICO OBJETIVO es agendar una cita (Virtual en Teams o Presencial) para los prospectos.

⛔ REGLAS CRÍTICAS (NO ROMPER):
1. NO respondas preguntas sobre destinos, precios, hoteles o turismo general. Si preguntan, di amablemente que un asesor experto se lo responderá en la cita y vuelve a intentar agendar.
2. Tu prioridad es CONVERTIR la conversación en una CITA agendada.
3. Tienes 2 intentos para agendar a clientes nuevos. Si fallan, transfiere (crea actividad).

🧠 LÓGICA DE ASIGNACIÓN (Sigue este orden):
1. **Identificar Cliente**: Usa `resolve_identity` con su teléfono/nombre.
2. **Cliente Agencia**: Si detectas que es una AGENCIA, asígnalo/agenda con el Asesor de Agencias (ID específico o búscalo).
3. **Cliente Existente en Bitrix**:
   - Si tiene un `ASSIGNED_BY_ID` (Responsable) válido (es uno de los asesores): OFRECE HORARIOS DE ESE ASESOR.
   - Si el responsable no es válido o no tiene: ASIGNA ALEATORIAMENTE (Usa un ID de asesor por defecto o rota entre disponibles).
   - *Nota*: Al usar `get_availability`, intenta usar el ID del responsable si lo tienes.
4. **Cliente Nuevo**: Asigna aleatoriamente a un asesor disponible.

📅 PROCESO DE AGENDAMIENTO:
1. **Validar Disponibilidad**: Usa `get_availability` para buscar huecos inmediatos.
2. **Ofrecer Opciones**: Da SIEMPRE 3 opciones de horario cercanas.
3. **Tipo de Cita**: Pregunta si prefiere **Virtual (Microsoft Teams)** o **Presencial**.
4. **Agendar**: Usa `schedule_meeting`.
   - Esto debe enviar el Link de la reunión (Teams) al correo (asume que la herramienta lo gestiona o confírmalo).
   - Informa de los recordatorios: "Te recordaremos 1 día antes y 1 hora antes (Virtual) / 2 horas antes (Presencial)".

🔄 MODIFICACIONES Y EXCEPCIONES:
- **Reagendar/Cancelar**: Si el cliente lo pide, usa `reschedule_event` o `cancel_event` y ofrece nuevas opciones.
- **Preguntas Post-Agendamiento**: Si ya agendó y pregunta algo más, dile que "Su asesor asignado atenderá esa duda puntualmente" y termina o transfiere (`create_activity`).
- **No Interesados en Cita (Info General)**: Si rehúsan agendar y solo quieren info general:
   - Identifica si tienen responsable. Si sí, crea actividad para ese responsable.
   - Si no, transfiere a un agente disponible (`create_activity` tipo "Solicitud Info").
- **Agencias**: Si se identifica como agencia, deriva inmediatamente al canal de agencias.

🛠️ USO DE HERRAMIENTAS:
- Identidad: `resolve_identity`, `enrich_identity`.
- Calendario: `get_availability`, `schedule_meeting`, `reschedule_event`, `cancel_event`.
- Gestión/Transferencia: `create_activity` (Úsalo para "Transferir" o "Dejar mensaje al asesor").
- Ventas: `detect_sales_stage` (Para saber si está listo para agendar).

TONO:
- MUY BREVE Y CONCISO.
- NO uses asteriscos (*) ni negritas para formatear. Texto plano y directo.
- Usa frases cortas. Evita párrafos largos.
- Profesional, directivo pero amable, enfocado 100% en cerrar la cita."""


# ─── Session Management ───────────────────────────────────────────

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
_sessions_lock = asyncio.Lock()


async def _cleanup_expired_sessions():
    """Limpia sesiones expiradas del cache."""
    expired = [cid for cid, s in _sessions.items() if s.is_expired()]
    for cid in expired:
        session = _sessions.pop(cid, None)
        if session:
            try:
                await session.agent.__aexit__(None, None, None)
            except Exception:
                pass
            print(f"  🧹 Sesión expirada limpiada para chat {cid}")


async def _create_new_session(chat_id: str) -> AgentSession:
    """Crea una nueva sesión de agente para un chat_id."""
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()

    # Obtener historial previo para semilla (si existe de sesiones anteriores)
    history_seed = format_history_str(chat_id)
    instruction = SYSTEM_PROMPT
    if history_seed:
        instruction = f"{SYSTEM_PROMPT}\n\n{history_seed}"

    # Iniciar el contexto de MCPApp
    agent_app = await app.run().__aenter__()

    travel_agent = Agent(
        name=f"travel_assistant_{chat_id}",
        instruction=instruction,
        functions=AGENT_FUNCTIONS,
        server_names=[],
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

    print(f"  🆕 Nueva sesión de agente creada para chat {chat_id} (provider: {llm_provider})")
    return session


async def get_response(user_message: str, chat_id: str) -> str:
    """
    Envía un mensaje al agente AI y retorna la respuesta.
    Reutiliza sesiones existentes para mantener contexto multi-turno nativo.
    """
    async with _sessions_lock:
        # Limpiar sesiones expiradas periódicamente
        await _cleanup_expired_sessions()

        session = _sessions.get(chat_id)

        # Si no hay sesión o expiró, crear una nueva
        if session is None or session.is_expired():
            if session and session.is_expired():
                try:
                    await session.agent.__aexit__(None, None, None)
                except Exception:
                    pass
            session = await _create_new_session(chat_id)
            _sessions[chat_id] = session

    # Marcar sesión como activa
    session.touch()

    try:
        # 1. Guardar mensaje del usuario en memoria persistente (JSON backup)
        add_message(chat_id, "user", user_message)

        # 2. Enviar al LLM (contexto multi-turno nativo de mcp-agent)
        result = await session.llm.generate_str(message=user_message)

        # 3. Guardar respuesta del bot en memoria persistente
        if result:
            add_message(chat_id, "assistant", result)

        return result or "Lo siento, no pude generar una respuesta."

    except Exception as e:
        print(f"❌ Error de mcp-agent: {e}")
        import traceback
        traceback.print_exc()

        # Si falla, invalidar la sesión para que se recree en el próximo intento
        async with _sessions_lock:
            _sessions.pop(chat_id, None)
            try:
                await session.agent.__aexit__(None, None, None)
            except Exception:
                pass

        return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."
