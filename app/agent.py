"""
Módulo de agente AI usando mcp-agent con GoogleAugmentedLLM (Gemini).
Implementa sesiones persistentes por chat_id para mantener contexto multi-turno nativo.
Incluye un ParallelObserverAgent para registrar actividades y tareas en segundo plano.
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
from tools.crm.enrich_identity import enrich_identity
from tools.crm.qualify_lead import qualify_lead
from tools.crm.find_duplicate import find_duplicate
from tools.crm.lead_add import lead_add
from tools.crm.lead_update import lead_update
from tools.crm.lead_convert import lead_convert
from tools.deal.deal_get import deal_get
from tools.deal.deal_list import deal_list
from tools.deal.deal_update_info import deal_update_info
from tools.deal.deal_move_stage import deal_move_stage
from tools.deal.deal_mark_closed import deal_mark_closed
from tools.deal.deal_add_note import deal_add_note
from tools.deal.deal_mark_closed import deal_mark_closed
from tools.calendar.calendar_get_types import calendar_get_types
from tools.calendar.calendar_event_list import calendar_event_list
from tools.calendar.calendar_availability_check import calendar_availability_check
from tools.calendar.calendar_event_create import calendar_event_create
from tools.calendar.calendar_event_update import calendar_event_update
from tools.calendar.calendar_event_delete import calendar_event_delete
from tools.calendar.calendar_event_set_reminder import calendar_event_set_reminder
from tools.catalog.catalog_list import catalog_list
from tools.catalog.catalog_category_list import catalog_category_list
from tools.catalog.catalog_product_list import catalog_product_list
from tools.catalog.catalog_product_get import catalog_product_get
from tools.catalog.catalog_product_search import catalog_product_search
from tools.catalog.deal_add_products import deal_add_products
from tools.catalog.deal_update_products import deal_update_products
from tools.catalog.deal_remove_product import deal_remove_product
from tools.document.document_template_list import document_template_list
from tools.document.document_generate import document_generate
from tools.document.document_list import document_list
from tools.document.document_download import document_download
from tools.drive.drive_folder_list import drive_folder_list
from tools.drive.drive_folder_create import drive_folder_create
from tools.drive.drive_file_upload import drive_file_upload
from tools.drive.drive_file_list import drive_file_list
from tools.drive.drive_file_download import drive_file_download
from tools.followup.lead_reactivate_by_client import lead_reactivate_by_client
from tools.followup.deal_detect_stage_for_client import deal_detect_stage_for_client
from tools.followup.deal_add_client_objection import deal_add_client_objection
from tools.followup.deal_update_probability_client import deal_update_probability_client
from tools.followup.lead_next_action_client import lead_next_action_client
from tools.followup.deal_next_action_client import deal_next_action_client
from tools.followup.deal_follow_up_schedule_client import deal_follow_up_schedule_client
from tools.followup.lead_follow_up_note_client import lead_follow_up_note_client
from tools.activity.activity_add import activity_add
from tools.task.task_create import task_create
from tools.openlines.session_send_message import session_send_message
from tools.openlines.session_transfer import session_transfer
from tools.openlines.session_finish import session_finish
from tools.openlines.crm_chat_link import crm_chat_link

# Lista de funciones (tools) disponibles para el agente PRINCIPAL
# Nota: NO incluye activity_add ni task_create, esos son del observador.
AGENT_FUNCTIONS = [
    enrich_identity, qualify_lead,
    find_duplicate, lead_add, lead_update, lead_convert,
    deal_get, deal_list, deal_update_info, deal_move_stage, deal_mark_closed, deal_add_note,
    calendar_get_types, calendar_event_list, calendar_availability_check,
    calendar_event_create, calendar_event_update, calendar_event_delete,
    calendar_event_set_reminder,
    catalog_list, catalog_category_list, catalog_product_list, catalog_product_get,
    catalog_product_search, deal_add_products, deal_update_products, deal_remove_product,
    document_template_list, document_generate, document_list, document_download,
    drive_folder_list, drive_folder_create, drive_file_upload, drive_file_list, drive_file_download,
    lead_reactivate_by_client, deal_detect_stage_for_client, deal_add_client_objection,
    deal_update_probability_client, lead_next_action_client, deal_next_action_client,
    deal_follow_up_schedule_client, lead_follow_up_note_client,
    session_send_message, session_transfer, session_finish, crm_chat_link
]

# Tools para el agente OBSERVADOR
OBSERVER_FUNCTIONS = [
    activity_add, task_create,
    # Puede necesitar algunas de lectura para contexto, pero idealmente se basa en el chat.
    # Le damos identity y deal info por si acaso necesita IDs.
    enrich_identity, deal_list
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
- **Preguntas Post-Agendamiento**: Si ya agendó y pregunta algo más, dile que "Su asesor asignado atenderá esa duda puntualmente" y termina o transfiere.
- **No Interesados en Cita (Info General)**: Si rehúsan agendar y solo quieren info general:
   - Identifica si tienen responsable. Si sí, crea actividad para ese responsable.
   - Si no, transfiere a un agente disponible (`create_activity` tipo "Solicitud Info").
- **Agencias**: Si se identifica como agencia, deriva inmediatamente al canal de agencias.

🛠️ USO DE HERRAMIENTAS:
- Identidad: `resolve_identity`, `enrich_identity`.
- CRM Leads: `find_duplicate` (buscar duplicados), `lead_add` (crear lead), `lead_update` (actualizar lead), `lead_convert` (convertir lead a contacto, empresa y/o deal), `qualify_lead` (calificar lead).
- Calendario: `get_availability`, `schedule_meeting`, `reschedule_event`, `cancel_event`.
- Ventas: `detect_sales_stage` (Para saber si está listo para agendar).
- Open Lines: `session_send_message` (enviar mensaje en sesión), `session_transfer` (transferir a operador/cola), `session_finish` (cerrar sesión).
- CRM-Chat: `crm_chat_link` (vincular conversación al CRM creando un Lead).
- Deal Tools: `deal_list`, `deal_get`, `deal_add_note`, `deal_update_info`, `deal_move_stage`, `deal_mark_closed`.

TONO:
- MUY BREVE Y CONCISO.
- NO uses asteriscos (*) ni negritas para formatear. Texto plano y directo.
- Usa frases cortas. Evita párrafos largos.
- Profesional, directivo pero amable, enfocado 100% en cerrar la cita."""


OBSERVER_SYSTEM_PROMPT = """Eres el Agente Observador de Calidad y Seguimiento de 'Viajes y Viajes'.
Eres un EXPERTO en Lead Management para Bitrix24.
Tu rol es OBSERVAR la conversación entre el usuario y el agente principal, y registrar calladamente actividades o tareas en el CRM para asegurar el seguimiento.

TUS OBJETIVOS:
1. Detectar eventos relevantes y registrarlos como NOTAS en el CRM (`activity_add`).
   - Ej: "Cliente pide cotización", "Cliente reagenda cita", "Cliente molesto", "Cliente nuevo saludando".
   - Regla: Cada interacción significativa debe quedar registrada, pero no abuses (no registres "Hola" o "OK" triviales).
2. Detectar necesidades de intervención HUMANA y crear TAREAS (`task_create`).
   - Ej: "Cliente pide hablar con supervisor", "Cliente hace pregunta compleja fuera del script", "Agente falló 2 veces en agendar".

HERRAMIENTAS DISPONIBLES:
- `activity_add`: Para notas y registro de historial.
- `task_create`: SOLO si se requiere acción humana explícita.
- `deal_list`, `enrich_identity`: Para buscar IDs si no los tienes claros.

REGLAS DE EJECUCIÓN:
- Eres invisible al usuario. NO generas respuestas de chat.
- Eres rápido y eficiente.
- Usa tu criterio experto: ¿Esto aporta valor al CRM? Si sí, regístralo.
- SIEMPRE intenta vincular la actividad al LEAD, DEAL o CONTACTO correcto (Owner ID). Si no sabes el ID, intenta deducirlo o búscalo, o usa uno genérico si es crítico.
"""

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


async def run_observer_agent(chat_id: str, user_message: str, ai_response: str):
    """
    Ejecuta el Agente Observador en paralelo para registrar actividades/tareas.
    """
    print(f"  👀 [Observer] Iniciando análisis para chat {chat_id}...")
    try:
        # Contexto para el observador
        context = (
            f"CHAT_ID: {chat_id}\n"
            f"USER MESSAGE: {user_message}\n"
            f"AGENT RESPONSE: {ai_response}\n\n"
            "Analiza esta interacción y decide si registrar Activity o Task."
        )

        # Usamos una instancia efímera o reutilizamos lógica similar, 
        # pero para simplicidad y aislamiento, creamos un agente rápido.
        # Nota: Idealmente el observador también tendría sesión, pero como es "stateless" 
        # en su análisis immediate (analiza el turno actual + historial si quisiera),
        # lo haremos one-shot o reusamos app context.
        
        async with app.run() as agent_app:
            observer = Agent(
                name=f"observer_{chat_id}",
                instruction=OBSERVER_SYSTEM_PROMPT,
                functions=OBSERVER_FUNCTIONS,
                server_names=[]
            )
            
            async with observer:
                # Usamos el mismo LLM provider configurado
                llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
                if llm_provider == "openai":
                    llm = await observer.attach_llm(OpenAIAugmentedLLM)
                else:
                    llm = await observer.attach_llm(GoogleAugmentedLLM)

                # Generamos acciones. El output del LLM aquí no se muestra al usuario, 
                # solo nos importan las tool calls que haga.
                result = await llm.generate_str(message=context)
                print(f"  👀 [Observer] Resultado: {result}")

    except Exception as e:
        print(f"  ❌ [Observer] Error: {e}")


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
        
        # Fallback si retorna vacío
        ai_response = result or "Lo siento, no pude generar una respuesta."

        # 3. Guardar respuesta del bot en memoria persistente
        add_message(chat_id, "assistant", ai_response)

        # 4. Lanzar Observador en Paralelo (Fire and forget)
        asyncio.create_task(run_observer_agent(chat_id, user_message, ai_response))

        return ai_response

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
