"""
MCP Server Local (STDIO) para Bot Viajes — Bitrix24 CRM.
Expone todas las tools existentes como MCP Tools, recursos de solo-lectura
como Resources, y plantillas de orquestación como Prompts.

Uso: python mcp_server.py  (se comunica por STDIO con mcp-agent)
"""
import sys
import os
import sys
import os

# Asegurar que el directorio raíz esté en el path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

# Cargar variables de entorno solo si existe el archivo (local dev)
# En producción (Cloud Run), las variables se inyectan directamente al entorno.
env_file = os.path.join(base_dir, ".env")
if os.path.exists(env_file):
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        sys.stderr.write("📁 .env cargado para desarrollo local (subproceso)\n")
    except Exception:
        pass

# Override print to use stderr globally for this process
# This prevents any print() call (including from libraries) from breaking 
# the MCP JSON-RPC protocol on stdout.
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)

# Debug logs para el subproceso
sys.stderr.write(f"🔧 MCP Server BaseDir: {base_dir}\n")

# Mask sensitive values in logs
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
if redis_url:
    masked_redis = redis_url.split('@')[-1] if '@' in redis_url else '***'
else:
    masked_redis = 'None'
sys.stderr.write(f"🔧 MCP Server REDIS_URL: {masked_redis}\n")
sys.stderr.write(f"🔧 MCP Server BITRIX_DOMAIN: {os.getenv('BITRIX_DOMAIN')}\n")

from mcp.server.fastmcp import FastMCP
from app.models import (
    CRMNoteRequest, CalendarEventCreateRequest,
    CalendarEventUpdateRequest, TaskCreateRequest, CRMActivityAddRequest,
    DriveResolveWorkspaceRequest, DocumentGenerateRequest, SessionTransferRequest,
    DriveFileUploadRequest, CatalogProductSearchRequest, CatalogProductListRequest,
    DealAddProductsRequest, NotifyAdvisorRequest, ChatProgressRequest,
    ManageLeadRequest, LeadConvertRequest, EnrichmentFields
)
from app.metrics import MetricsService
import time
import functools

def track_tool_usage(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        try:
            return await func(*args, **kwargs)
        except Exception:
            success = False
            raise
        finally:
            duration = (time.time() - start_time) * 1000
            try:
                ms = await MetricsService.get_instance()
                from app.context_vars import member_id_var
                tenant = member_id_var.get() or "unknown"
                await ms.log_tool_usage(tenant, func.__name__, success, duration)
            except Exception as e:
                sys.stderr.write(f"⚠️ Metrics error: {e}\n")
    return wrapper

# ─── Inicializar servidor ─────────────────────────────────────────
mcp = FastMCP(
    name="bitrix_crm",
)

async def _set_context(chat_id=None):
    """Establece el contexto de tenant (member_id) para la ejecución actual."""
    if chat_id:
        from app.token_manager import get_token_manager
        tm = await get_token_manager()
        m_id = await tm.get_member_id_from_chat(chat_id)
        if m_id:
            from app.context_vars import member_id_var
            member_id_var.set(m_id)
            # También poner en os.environ para tools legacy que usen os.getenv
            os.environ["BITRIX_MEMBER_ID"] = m_id
            sys.stderr.write(f"🌐 Contexto establecido para chat {chat_id}: {m_id}\n")

# ═══════════════════════════════════════════════════════════════════
# TOOLS — Funciones de acción que modifican o consultan Bitrix24
# ═══════════════════════════════════════════════════════════════════

# ─── CRM / Leads ──────────────────────────────────────────────────


@mcp.tool()
@track_tool_usage
async def manage_lead(req: ManageLeadRequest) -> str:
    """Gestiona LEADS de forma inteligente: Busca duplicados, actualiza o crea."""
    try:
        await _set_context(req.chat_id)
        from tools.crm.manage_lead import manage_lead as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en manage_lead: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en manage_lead: {e}"

@mcp.tool()
@track_tool_usage
async def crm_add_note(req: CRMNoteRequest) -> str:
    """Añade una NOTA (calificación, intereses, score) a Lead, Contacto o Negocio."""
    try:
        from tools.crm.crm_add_note import crm_add_note as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en crm_add_note: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en crm_add_note: {e}"



@mcp.tool()
@track_tool_usage
async def lead_get(lead_id: int) -> str:
    """Usa esta tool para LEER toda la información detallada de un Lead específico."""
    try:
        from tools.crm.lead_get import lead_get as _fn
        return await _fn(lead_id=lead_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_get: {e}"

@mcp.tool()
@track_tool_usage
async def lead_convert(req: LeadConvertRequest) -> str:
    """CONVIERTE Lead en Negocio, Contacto y/o Empresa."""
    try:
        await _set_context(req.chat_id)
        from tools.crm.lead_convert import lead_convert as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_convert: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_convert: {e}"

@mcp.tool()
@track_tool_usage
async def enrich_entity(entity_id: int, entity_type: str, fields: EnrichmentFields) -> str:
    """Enriquece Lead/Deal con datos adicionales. Permite campos personalizados UF_CRM_*."""
    try:
        from tools.crm.enrich_entity import enrich_entity as _fn
        # Pasamos el dict original (con los campos extra) a la tool
        all_fields = fields.model_dump(exclude_unset=True)
        all_fields.update(fields.model_extra or {})
        return await _fn(entity_id=entity_id, entity_type=entity_type, fields=all_fields)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en enrich_entity: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en enrich_entity: {e}"
@mcp.tool()
@track_tool_usage
async def lead_qualify(lead_id: int) -> str:
    """Usa esta tool para CALIFICAR y AVANZAR un Lead en el embudo.
    Evalúa si tiene datos suficientes para pasar de 'NEW' a 'IDENTIFICACIÓN' o 'ASIGNACIÓN'."""
    try:
        from tools.crm.lead_qualify import lead_qualify as _fn
        return await _fn(lead_id=lead_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_qualify: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_qualify: {e}"


# ─── CRM / Contacts ──────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def contact_get(contact_id: int) -> str:
    """Usa esta tool para LEER toda la información detallada de un Contacto específico."""
    try:
        from tools.crm.contact_get import contact_get as _fn
        return await _fn(contact_id=contact_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en contact_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en contact_get: {e}"


# ─── CRM / Deals ──────────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def deal_get(deal_id: int) -> str:
    """Usa esta tool para LEER toda la información detallada de un Deal específico (Monto, etapa, cliente asignado, etc)."""
    try:
        from tools.deal.deal_get import deal_get as _fn
        return await _fn(deal_id=deal_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_get: {e}"

@mcp.tool()
@track_tool_usage
async def deal_list(filter_status: str = None, limit: int = 10) -> str:
    """Usa esta tool para LISTAR Deals activos, filtrados por etapa si es necesario."""
    try:
        from tools.deal.deal_list import deal_list as _fn
        return await _fn(filter_status=filter_status, limit=limit)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_list: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_list: {e}"


@mcp.tool()
@track_tool_usage
async def deal_move_stage(deal_id: int, stage_id: str) -> str:
    """Usa esta tool para MOVER el Deal a una nueva etapa (ej: 'NEW', 'PREPARATION', 'PREPAYMENT')."""
    try:
        from tools.deal.deal_move_stage import deal_move_stage as _fn
        return await _fn(deal_id=deal_id, stage_id=stage_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_move_stage: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_move_stage: {e}"

@mcp.tool()
@track_tool_usage
async def company_get(company_id: int) -> str:
    """Usa esta tool para LEER toda la información detallada de una Empresa específica."""
    try:
        from tools.crm.company_get import company_get as _fn
        return await _fn(company_id=company_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en company_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en company_get: {e}"

# ─── CRM / Metadata ───────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def crm_fields_get(entity_type: str) -> str:
    """Usa esta tool para ver el ESQUEMA de campos (nombres técnicos y etiquetas) de una entidad (LEAD, DEAL, CONTACT, COMPANY)."""
    try:
        from tools.crm.crm_fields_get import crm_fields_get as _fn
        return await _fn(entity_type=entity_type)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en crm_fields_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en crm_fields_get: {e}"

@mcp.tool()
@track_tool_usage
async def crm_stages_list(entity_type: str = "DEAL") -> str:
    """Usa esta tool para ver las ETAPAS o estados disponibles para una entidad (LEAD o DEAL)."""
    try:
        from tools.crm.crm_stages_list import crm_stages_list as _fn
        return await _fn(entity_type=entity_type)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en crm_stages_list: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en crm_stages_list: {e}"

# ─── Calendar ─────────────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def calendar_event_list(from_date: str = None, to_date: str = None) -> str:
    """Usa esta tool para LEER LA AGENDA y saber qué reuniones hay programadas en un rango."""
    from tools.calendar.calendar_event_list import calendar_event_list as _fn
    return await _fn(from_date=from_date, to_date=to_date)

@mcp.tool()
@track_tool_usage
async def calendar_availability_check(start_time: str, end_time: str) -> str:
    """Usa esta tool para VERIFICAR DISPONIBILIDAD antes de agendar. Retorna si el horario está libre u ocupado."""
    try:
        from tools.calendar.calendar_availability_check import calendar_availability_check as _fn
        return await _fn(start_time=start_time, end_time=end_time)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_availability_check: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_availability_check: {e}"

@mcp.tool()
@track_tool_usage
async def calendar_event_create(req: CalendarEventCreateRequest) -> str:
    """Crea cita en el calendario. TÍTULO: '[Destino] - [Nombre]'."""
    try:
        from tools.calendar.calendar_event_create import calendar_event_create as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_create: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_create: {e}"

@mcp.tool()
@track_tool_usage
async def calendar_event_update(req: CalendarEventUpdateRequest) -> str:
    """MODIFICA o REPROGRAMA una reunión existente."""
    try:
        from tools.calendar.calendar_event_update import calendar_event_update as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_update: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_update: {e}"

@mcp.tool()
@track_tool_usage
async def calendar_event_delete(event_id: int) -> str:
    """Usa esta tool para CANCELAR/BORRAR una reunión."""
    try:
        from tools.calendar.calendar_event_delete import calendar_event_delete as _fn
        return await _fn(event_id=event_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_delete: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_delete: {e}"

@mcp.tool()
@track_tool_usage
async def calendar_event_get(event_id: int) -> str:
    """Usa esta tool para LEER todos los detalles de una cita específica en el calendario."""
    try:
        from tools.calendar.calendar_event_get import calendar_event_get as _fn
        return await _fn(event_id=event_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_get: {e}"

# ─── Catalog / Products ──────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def catalog_product_list(req: CatalogProductListRequest) -> str:
    """LISTAR PRODUCTOS dentro de una categoría específica."""
    try:
        from tools.catalog.catalog_product_list import catalog_product_list as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en catalog_product_list: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en catalog_product_list: {e}"

@mcp.tool()
@track_tool_usage
async def catalog_product_get(product_id: int) -> str:
    """Usa esta tool para ver DETALLES COMPLETOS de un producto específico por ID."""
    from tools.catalog.catalog_product_get import catalog_product_get as _fn
    return await _fn(product_id=product_id)

@mcp.tool()
@track_tool_usage
async def catalog_product_search(req: CatalogProductSearchRequest) -> str:
    """BUSCAR PRODUCTOS por nombre o palabra clave."""
    try:
        from tools.catalog.catalog_product_search import catalog_product_search as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en catalog_product_search: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en catalog_product_search: {e}"

@mcp.tool()
@track_tool_usage
async def deal_add_products(req: DealAddProductsRequest) -> str:
    """AGREGAR PRODUCTOS a un Deal existente."""
    try:
        from tools.catalog.deal_add_products import deal_add_products as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_add_products: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_add_products: {e}"


@mcp.tool()
@track_tool_usage
async def deal_remove_product(row_id: int) -> str:
    """Usa esta tool para ELIMINAR un producto de un Deal."""
    from tools.catalog.deal_remove_product import deal_remove_product as _fn
    return await _fn(row_id=row_id)

# ─── Document ─────────────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def document_generate(req: DocumentGenerateRequest) -> str:
    """GENERA documento (contrato, cotización) basado en plantilla."""
    try:
        from tools.document.document_generate import document_generate as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en document_generate: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en document_generate: {e}"

@mcp.tool()
@track_tool_usage
async def document_list(entity_id: int, entity_type_id: int = 2) -> str:
    """Usa esta tool para VER qué documentos ya fueron generados para un Lead o Deal."""
    from tools.document.document_list import document_list as _fn
    return await _fn(entity_id=entity_id, entity_type_id=entity_type_id)

@mcp.tool()
@track_tool_usage
async def document_download(document_id: int) -> str:
    """Usa esta tool para DESCARGAR un documento ya generado y obtener su URL."""
    from tools.document.document_download import document_download as _fn
    return await _fn(document_id=document_id)

# ─── Drive ────────────────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def drive_resolve_workspace(req: DriveResolveWorkspaceRequest) -> str:
    """Resuelve o crea carpeta de trabajo para el cliente."""
    try:
        from tools.drive.drive_resolve_workspace import drive_resolve_workspace as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en drive_resolve_workspace: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en drive_resolve_workspace: {e}"

@mcp.tool()
@track_tool_usage
async def drive_folder_create(name: str, parent_id: int = None) -> str:
    """Usa esta tool para CREAR una nueva carpeta en Bitrix24 Drive."""
    from tools.drive.drive_folder_create import drive_folder_create as _fn
    return await _fn(name=name, parent_id=parent_id)

@mcp.tool()
@track_tool_usage
async def drive_file_upload(req: DriveFileUploadRequest) -> str:
    """SUBIR un archivo al Drive de Bitrix24."""
    try:
        from tools.drive.drive_file_upload import drive_file_upload as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en drive_file_upload: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en drive_file_upload: {e}"

@mcp.tool()
@track_tool_usage
async def drive_file_list(folder_id: int) -> str:
    """Usa esta tool para VER los archivos dentro de una carpeta del Drive."""
    from tools.drive.drive_file_list import drive_file_list as _fn
    return await _fn(folder_id=folder_id)

@mcp.tool()
@track_tool_usage
async def drive_file_download(file_id: int) -> str:
    """Usa esta tool para DESCARGAR un archivo del Drive y obtener su URL."""
    from tools.drive.drive_file_download import drive_file_download as _fn
    return await _fn(file_id=file_id)

# ─── Followup ─────────────────────────────────────────────────────

@mcp.tool()
@track_tool_usage
async def lead_reactivate_by_client(lead_id: int) -> str:
    """Usa esta tool cuando un cliente con Lead anterior vuelve a escribir. Reactiva el Lead cambiando su STATUS_ID."""
    try:
        from tools.crm.lead_reactivate_by_client import lead_reactivate_by_client as _fn
        return await _fn(lead_id=lead_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_reactivate_by_client: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_reactivate_by_client: {e}"

@mcp.tool()
@track_tool_usage
async def deal_update_probability_client(deal_id: int, probability: int) -> str:
    """Usa esta tool para ACTUALIZAR la probabilidad de cierre de un Deal (0-100)."""
    try:
        from tools.deal.deal_update_probability_client import deal_update_probability_client as _fn
        return await _fn(deal_id=deal_id, probability=probability)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_update_probability_client: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_update_probability_client: {e}"

# ─── Openlines ────────────────────────────────────────────────────


@mcp.tool()
@track_tool_usage
async def session_transfer(req: SessionTransferRequest) -> str:
    """TRANSFERIR conversación a HUMANO (user_id o cola)."""
    try:
        await _set_context(req.chat_id)
        from tools.openlines.session_transfer import session_transfer as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_transfer: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_transfer: {e}"

@mcp.tool()
@track_tool_usage
async def chat_send_progress(req: ChatProgressRequest) -> str:
    """Envía un mensaje de CORTESÍA o PROGRESO al cliente (ej: 'Dame un momento mientras...')"""
    try:
        await _set_context(req.chat_id)
        from tools.openlines.chat_send_progress import chat_send_progress as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en chat_send_progress: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en chat_send_progress: {e}"

@mcp.tool()
@track_tool_usage
async def advisor_notify(req: NotifyAdvisorRequest) -> str:
    """Envía una NOTIFICACIÓN directa a un asesor (pop-up en Bitrix24)."""
    try:
        from tools.openlines.advisor_notify import advisor_notify as _fn
        return await _fn(**req.model_dump())
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en advisor_notify: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en advisor_notify: {e}"

@mcp.prompt()
async def data_elicitation_strategy(missing_field: str, operation: str = "gestión") -> str:
    """Guía: Cómo pedir datos faltantes (Elicitación) con un tono profesional y servicial."""
    return f"""INSTRUCCIÓN: Elicitación de Datos Proactiva
    
Si necesitas el campo '{missing_field}' para completar la {operation}:

1. **Informa con cortesía**: Explica brevemente por qué es necesario (ej: "Para poder procesar tu cotización..." o "Para asegurar tu lugar en la reunión...").
2. **Pide el dato**: Haz la pregunta de forma clara y directa.
3. **Mantén el flujo**: Asegura al cliente que una vez proporcione el dato, terminarás el proceso de inmediato.

Ejemplo: "¡Excelente! Para poder generar tu cotización formal ahora mismo, solo necesito que me confirmes tu correo electrónico. ¿Podrías proporcionármelo?"
"""

@mcp.tool()
@track_tool_usage
async def session_finish(chat_id: int) -> str:
    """Usa esta tool para CERRAR la sesión de chat cuando la conversación haya terminado."""
    await _set_context(chat_id)
    from tools.openlines.session_finish import session_finish as _fn
    return await _fn(chat_id=chat_id)



@mcp.tool()
@track_tool_usage
async def session_crm_get(chat_id: int) -> str:
    """Usa esta tool para VERIFICAR si ya existe un Lead vinculado a la sesión actual ANTES de crear uno nuevo."""
    try:
        await _set_context(chat_id)
        from tools.openlines.session_crm_get import session_crm_get as _fn
        return await _fn(chat_id=chat_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_crm_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_crm_get: {e}"

@mcp.tool()
@track_tool_usage
async def session_operator_list(config_id: int = 1) -> str:
    """Lista los operadores ONLINE de la línea abierta. Úsalo ANTES de transferir para saber si hay alguien disponible."""
    from tools.openlines.session_operator_list import session_operator_list as _fn
    return await _fn(config_id=config_id)

@mcp.tool()
@track_tool_usage
async def session_queue_info(config_id: int = 1) -> str:
    """Consulta la config de la cola de atención: cuántos operadores online, tiempo de rotación y estimado de espera."""
    from tools.openlines.session_queue_info import session_queue_info as _fn
    return await _fn(config_id=config_id)

@mcp.tool()
@track_tool_usage
async def session_history_read(session_id: int) -> str:
    """Lee el historial de una sesión de forma SILENCIOSA (sin que el bot aparezca en el chat).
    Ideal para analizar la charla operador-cliente y generar notas internas con sugerencias."""
    from tools.openlines.session_history_read import session_history_read as _fn
    return await _fn(session_id=session_id)


# ─── Activity / Tasks (Observer) ─────────────────────────────────

@mcp.tool()
@track_tool_usage
async def task_create(req: TaskCreateRequest) -> str:
    """CREAR TAREAS de seguimiento interno vinculado a Lead/Deal."""
    try:
        from tools.task.task_create import task_create as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en task_create: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en task_create: {e}"

@mcp.tool()
@track_tool_usage
async def task_list(entity_id: int = None, entity_type: str = "LEAD") -> str:
    """Lista las tareas de Bitrix24, opcionalmente filtradas por una entidad CRM."""
    from tools.task.task_list import task_list as _fn
    return await _fn(entity_id=entity_id, entity_type=entity_type)

# ─── Activity / CRM Activities ───────────────────────────────────

@mcp.tool()
@track_tool_usage
async def crm_activity_add(req: CRMActivityAddRequest) -> str:
    """AGREGAR actividad (Llamada, Reunión) al CRM."""
    try:
        from tools.activity.crm_activity_add import crm_activity_add as _fn
        return await _fn(**req.model_dump(exclude_unset=True))
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en crm_activity_add: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en crm_activity_add: {e}"

@mcp.tool()
@track_tool_usage
async def crm_activity_list(entity_id: int, entity_type: str) -> str:
    """Lista las actividades registradas para un Lead o Deal."""
    from tools.activity.crm_activity_list import crm_activity_list as _fn
    return await _fn(entity_id=entity_id, entity_type=entity_type)




# ═══════════════════════════════════════════════════════════════════
# RESOURCES — Datos de solo-lectura para contexto
# ═══════════════════════════════════════════════════════════════════

@mcp.resource("bitrix://catalogs")
async def resource_catalog_list() -> str:
    """Lista de catálogos disponibles en Bitrix24."""
    from tools.catalog.catalog_list import catalog_list as _fn
    return await _fn()

@mcp.resource("bitrix://catalog/{catalog_id}/categories")
async def resource_catalog_categories(catalog_id: int) -> str:
    """Categorías/secciones de un catálogo específico."""
    from tools.catalog.catalog_category_list import catalog_category_list as _fn
    return await _fn(catalog_id=catalog_id)

@mcp.resource("bitrix://calendar/types")
async def resource_calendar_types() -> str:
    """Tipos de calendario disponibles (personal, grupo, recurso)."""
    from tools.calendar.calendar_get_types import calendar_get_types as _fn
    return await _fn()

@mcp.resource("bitrix://documents/templates")
async def resource_document_templates() -> str:
    """Plantillas de documentos disponibles para generar contratos/cotizaciones."""
    from tools.document.document_template_list import document_template_list as _fn
    return await _fn()

@mcp.resource("bitrix://crm/fields/{entity_type}")
async def resource_crm_fields(entity_type: str) -> str:
    """Esquema de campos para una entidad CRM (LEAD, DEAL, CONTACT, COMPANY)."""
    from tools.crm.crm_fields_get import crm_fields_get as _fn
    return await _fn(entity_type=entity_type)

@mcp.resource("bitrix://crm/stages/{entity_type}")
async def resource_crm_stages(entity_type: str) -> str:
    """Etapas o estados de un proceso CRM (LEAD, DEAL)."""
    from tools.crm.crm_stages_list import crm_stages_list as _fn
    return await _fn(entity_type=entity_type)

@mcp.resource("bitrix://crm/lead/{lead_id}")
async def resource_crm_lead_details(lead_id: int) -> str:
    """Detalles completos de un Lead específico."""
    from tools.crm.lead_get import lead_get as _fn
    return await _fn(lead_id=lead_id)

@mcp.resource("bitrix://crm/deal/{deal_id}")
async def resource_crm_deal_details(deal_id: int) -> str:
    """Detalles completos de un Negocio (Deal) específico."""
    from tools.deal.deal_get import deal_get as _fn
    return await _fn(deal_id=deal_id)

@mcp.resource("bitrix://crm/contact/{contact_id}")
async def resource_crm_contact_details(contact_id: int) -> str:
    """Detalles completos de un Contacto específico."""
    from tools.crm.contact_get import contact_get as _fn
    return await _fn(contact_id=contact_id)

@mcp.resource("bitrix://crm/company/{company_id}")
async def resource_crm_company_details(company_id: int) -> str:
    """Detalles completos de una Empresa específica."""
    from tools.crm.company_get import company_get as _fn
    return await _fn(company_id=company_id)

@mcp.resource("bitrix://calendar/event/{event_id}")
async def resource_calendar_event_details(event_id: int) -> str:
    """Detalles de una cita específica en el calendario."""
    from tools.calendar.calendar_event_get import calendar_event_get as _fn
    return await _fn(event_id=event_id)

@mcp.resource("bitrix://crm/{entity_type}/{entity_id}/documents")
async def resource_entity_documents(entity_type: str, entity_id: int) -> str:
    """Lista de documentos generados para una entidad CRM (LEAD, DEAL)."""
    etype_id = 1 if entity_type.upper() == "LEAD" else 2
    from tools.document.document_list import document_list as _fn
    return await _fn(entity_id=entity_id, entity_type_id=etype_id)

@mcp.resource("bitrix://catalog/category/{section_id}/products")
async def resource_catalog_products(section_id: int) -> str:
    """Productos disponibles dentro de una categoría específica."""
    from tools.catalog.catalog_product_list import catalog_product_list as _fn
    return await _fn(section_id=section_id)

@mcp.resource("bitrix://openlines/session/{chat_id}/crm")
async def resource_session_crm(chat_id: int) -> str:
    """Verifica qué Lead o Deal está vinculado a la sesión de chat actual."""
    from tools.openlines.session_crm_get import session_crm_get as _fn
    return await _fn(chat_id=chat_id)


@mcp.resource("bitrix://crm/{entity_type}/{entity_id}/tasks")
async def resource_entity_tasks(entity_type: str, entity_id: int) -> str:
    """Lista de tareas activas vinculadas a una entidad CRM (LEAD, DEAL, etc.)."""
    from tools.task.task_list import task_list as _fn
    return await _fn(entity_id=entity_id, entity_type=entity_type)

@mcp.resource("bitrix://drive/folder/{folder_id}/items")
async def resource_drive_folder_items(folder_id: int) -> str:
    """Lista de archivos y carpetas dentro de una ubicación del Drive."""
    from tools.drive.drive_file_list import drive_file_list as _fn
    return await _fn(folder_id=folder_id)


# ═══════════════════════════════════════════════════════════════════
# PROMPTS — Plantillas de orquestación para guiar al agente
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
async def identity_management_strategy(chat_id: int, name: str = "", phone: str = "", email: str = "") -> str:
    """Guía: Prioridad de aceptación, actualización de datos y disparador de Lead."""
    return f"""INSTRUCCIÓN: Gestión de Sesión, Identidad y Prospectos
    
Sigue esta jerarquía obligatoria para gestionar al cliente:
    
1. **DISPARADOR DE LEAD (¡CRITICAL!)**: Si el cliente ya dio su **NOMBRE** y/o **TELÉFONO** ({name or 'Desconocido'}, {phone or 'Desconocido'}) y NO hay un Lead vinculado:
    - **Debes llamar a `manage_lead` de inmediato**.
    - **IMPORTANTE**: Asegúrate de pasar el `name` y el `phone` como argumentos a `manage_lead`. Esto evitará duplicados y creará o actualizará el registro según corresponda.
    - Esto garantiza que el cliente aparezca en la sección de **Prospectos** (Leads) de Bitrix24.
    
2. **EMAIL OBLIGATORIO**: Si el cliente quiere agendar una cita, **DEBES** obtener su email primero. Es indispensable para enviar el acceso a la reunión.
    
3. **ACTUALIZACIÓN DE DATOS**: Si el cliente da un nuevo dato clave (nombre corregido, teléfono), usa `manage_lead`.
    
4. **ENRIQUECIMIENTO PROACTIVO**: Usa `enrich_entity` inmediatamente cuando el cliente mencione datos secundarios como su **EMAIL**, **PRESUPUESTO**, **DESTINOS PREFERIDOS** o **CARGO**. No esperes a que termine la charla.
    
5. **Respuesta**: Sigue con el agendamiento. Tus respuestas se enviarán por duplicado para garantizar visibilidad total.
"""

@mcp.prompt()
async def qualify_and_assign(client_name: str = "", client_phone: str = "", client_email: str = "") -> str:
    """Guía de orquestación: Buscar duplicados → calificar con nota → crear o actualizar Lead."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Gestionar Lead
    
Datos del cliente:
- Nombre: {client_name or 'No proporcionado'}
- Teléfono: {client_phone or 'No proporcionado'}
- Email: {client_email or 'No proporcionado'}
    
PASOS A SEGUIR:
1. Usa `manage_lead` directamente. Esta herramienta buscará duplicados y creará o actualizará el Lead según corresponda.
2. Usa `crm_add_note` para registrar descubrimientos, intención o calificación en el historial.
3. Si el interés es de compra inmediata, usa `lead_convert` para pasarlo a Negocio (Deal).
    
IMPORTANTE: Confía en `manage_lead` para la gestión de identidad."""


@mcp.prompt()
async def schedule_meeting(client_name: str = "", preferred_date: str = "", meeting_type: str = "virtual") -> str:
    """Guía de orquestación: Verificar disponibilidad → ofrecer opciones → agendar → confirmar."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Agendar Reunión

Cliente: {client_name or 'Desconocido'}
Fecha preferida: {preferred_date or 'Flexible'}
Tipo: {meeting_type}

PASOS A SEGUIR:
1. **Verificar Calendario**: Usa el recurso `bitrix://calendar/types` para identificar el ID del calendario adecuado (ej: 'General', 'Ventas').
2. Usa `calendar_availability_check` para el rango de fechas solicitado.
3. **SI EL CLIENTE ES UN LEAD**: Ejecuta `lead_convert` para crear el Negocio (Deal) ANTES de agendar.
4. Con el DEAL_ID y el `section_id` del calendario (USA 0 si no estás seguro o si es para el calendario principal), usa `calendar_event_create` para agendar.
5. Confirma la cita al cliente resaltando que ya está en agenda.

NOTA: La tool `calendar_event_create` ya incluye el recordatorio de 60 min por defecto y rintentará con sección 0 si falla.
"""


@mcp.prompt()
async def avoid_duplicates(phone: str = "", email: str = "") -> str:
    """Guía: Verificar si el cliente ya existe antes de crear un nuevo Lead."""
    return f"""INSTRUCCIÓN: Prevención de Duplicados
    
Para evitar duplicados, SIEMPRE usa `manage_lead`.
    
PASOS:
1. Ejecuta `manage_lead` pasando el teléfono ({phone}) y/o email ({email}).
2. La herramienta detectará automáticamente si el cliente ya existe y lo actualizará, o creará uno nuevo si es necesario.
3. NO uses otras herramientas de creación manual.
"""

@mcp.prompt()
async def convert_to_lead(chat_id: int, name: str = "", phone: str = "", interest: str = "") -> str:
    """Guía: Convertir una conversación del Contact Center en un Lead formal del CRM."""
    return f"""INSTRUCCIÓN: Transición a CRM (Lead Creation)
    
Una vez identificado el interés y los datos del cliente ({name}, {phone}, Interés: {interest}), el siguiente paso es formalizarlo en el CRM.
    
PASOS:
1. Usa `manage_lead` proporcionando el `chat_id` ({chat_id}), `name` y `phone`.
2. El sistema creará o actualizará el Lead y lo VINCULARÁ automáticamente a esta conversación.
3. Esto permite que el historial del chat sea visible para los vendedores dentro de la ficha del Lead.
4. Una vez gestionado, puedes informar al cliente que un asesor revisará su solicitud.
"""


@mcp.prompt()
async def check_crm_status(chat_id: int) -> str:
    """Guía: Verificar si el chat ya tiene CRM."""
    return f"""INSTRUCCIÓN: Gestión de CRM en Chat
    
PASOS:
1. Usa `session_crm_get` para ver si el chat ({chat_id}) ya tiene un Lead o Deal vinculado.
2. Si existe un vínculo, evita duplicar esfuerzos. Si no existe, puedes proceder con la calificación."""

@mcp.prompt()
async def close_or_transfer_session(chat_id: int, reason: str = "") -> str:
    """Guía: Finalizar o transferir una conversación según la necesidad."""
    return f"""INSTRUCCIÓN: Cierre o Transferencia
    
Situación: {reason or 'Fin de atención'}
    
ACCIONES:
- Si el problema se resolvió o la venta terminó: Usa `session_finish` para cerrar el chat ({chat_id}).
- Si el cliente pide un humano o es un tema complejo: Usa `session_transfer` para pasar el chat a la cola de agentes.
"""

@mcp.prompt()
async def manage_deal(deal_id: str = "", action: str = "") -> str:
    """Guía de orquestación: Obtener deal → actualizar info → mover etapa → agregar productos."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Gestionar Deal

Deal ID: {deal_id or 'Por determinar'}
Acción solicitada: {action or 'Revisar estado'}

PASOS A SEGUIR:
1. Usa `deal_get` para obtener información completa del Deal.
2. Según la acción:
    - Mover etapa → `deal_move_stage`
    - Gestionar Carrito → `catalog_product_search` → `deal_add_products` / `deal_remove_product`
   - Agregar nota → `crm_add_note` (entity_type='DEAL')
3. Registra siempre un resumen de la gestión con `crm_add_note`.

NOTA: Siempre verificar el estado actual antes de hacer cambios. PROHIBIDO CERRAR NEGOCIOS.
"""


@mcp.prompt()
async def conversion_strategy(lead_id: int, chat_id: int = None, is_b2b: bool = False) -> str:
    """Guía: Cuándo y cómo realizar la conversión de Lead a Deal/Contacto."""
    return f"""INSTRUCCIÓN: El Salto a Negocio (Conversion)
    
La SEÑAL para convertir es el AGENDAMIENTO de una cita o una petición formal de cotización.
    
PASOS:
1. Determina si es B2C (Individuo) o B2B (Empresa).
2. Ejecuta `lead_convert` con los flags apropiados:
   - B2C Estándar: `create_deal=True`, `create_contact=True`
   - B2B Estándar: `create_deal=True`, `create_contact=True`, `create_company=True`
   - Solo Base de Datos: `create_deal=False`, `create_contact=True`
3. Recibirás los IDs de las entidades creadas.
4. Usa el DEAL_ID para gestionar la venta.
"""
@mcp.prompt()
async def funnel_advancement_strategy(lead_id: int) -> str:
    """Guía: Cómo y cuándo avanzar al cliente en las etapas del CRM."""
    return f"""INSTRUCCIÓN: Avance de Embudo (Sales Funnel)
    
Tu objetivo es que el cliente no se quede estancado en la etapa inicial.
    
PASOS:
1. **Tras capturar Datos**: En cuanto uses `manage_lead` o `enrich_entity` y tengas Nombre + (Teléfono o Email), ejecuta `lead_qualify`({lead_id}).
2. **Tras Asignación**: Si detectas que un humano ha sido asignado o si el cliente ya está calificado, usa `lead_qualify` para moverlo a 'ASIGNACIÓN'.
3. **Cierre**: Mantén al cliente informado de que su perfil está siendo procesado para darle la mejor atención.
"""

@mcp.prompt()
async def update_lead_info(lead_id: int, details: str = "") -> str:
    """Guía: Actualizar información de un Lead existente."""
    return f"""INSTRUCCIÓN: Actualización de Lead
    
Si el cliente proporciona nuevos datos (ej: {details or 'un segundo teléfono'}) para un Lead ya existente ({lead_id}), usa `lead_update`.
    
PASOS:
1. Identifica qué campos necesitas cambiar.
2. Usa `lead_update` pasando el ID y un diccionario con los campos (ej: {{"PHONE": "..."}}).
3. Confirma al cliente que sus datos han sido actualizados.
"""

@mcp.prompt()
async def add_crm_note(entity_id: int, entity_type: str = "LEAD") -> str:
    """Guía: Registrar información importante en el historial del CRM."""
    return f"""INSTRUCCIÓN: Registro de Notas en CRM
    
Usa `crm_add_note` para dejar constancia de cualquier detalle relevante que no encaje en un campo estándar (ej: calificación del lead, preferencias de viaje, presupuesto mencionado, score de interés).
    
PASOS:
1. Define la entidad ({entity_type}) y su ID ({entity_id}).
2. Escribe un mensaje claro y profesional.
3. Esto ayuda a que los compañeros que vean la ficha del cliente entiendan el contexto rápidamente.
"""

@mcp.prompt()
async def quote_generation_flow(deal_id: int, product_name: str = "") -> str:
    """Guía: Buscar producto → añadir al deal → generar PDF de cotización."""
    return f"""INSTRUCCIÓN: Creación de Propuesta Comercial (Cotización)
    
PASOS PARA UNA COTIZACIÓN EXITOSA:
1. **Buscar**: Usa `catalog_product_search` para encontrar el ID del producto (ej: {product_name or '...'}) y su precio.
2. **Auto-Exploración**: Si no encuentras el producto exacto, usa el recurso `bitrix://catalogs` y luego `resource_catalog_products` para descubrir qué hay disponible en el inventario.
3. **Añadir**: Usa `deal_add_products` para vincular ese producto al Deal ({deal_id}).
4. **Plantilla**: Usa `document_template_list` para ver qué plantillas de cotización hay disponibles (entity_type_id=2).
5. **Generar**: Usa `document_generate` con el `template_id` elegido y el `entity_id`={deal_id}.
6. **Entregar**: Usa `document_download` para darle los links de PDF/Word al cliente.
7. **Nota**: Registra el envío de la cotización con `crm_add_note`.
"""

@mcp.prompt()
async def catalog_discovery_and_sales() -> str:
    """Guía: Explorar catálogos y categorías cuando el cliente no es específico."""
    return f"""INSTRUCCIÓN: Descubrimiento Dinámico de Productos
    
Si el cliente pregunta "¿qué tienes?" o no eres capaz de encontrar algo específico, sigue esta ruta lógica:

1. **Listar Catálogos**: Usa el recurso `bitrix://catalogs` para ver las áreas generales (ej: Paquetes, Hoteles).
2. **Explorar Categorías**: Con el `catalog_id` cottonido, usa el recurso `bitrix://catalog/ID/categories`.
3. **Ver Productos**: Usa `resource_catalog_products` para listar los productos de una categoría de interés.
4. **Ofrecer**: Presenta las opciones al cliente resaltando precios y beneficios.

OBJETIVO: Ser proactivo y no limitarse a búsquedas exactas fallidas."""

@mcp.prompt()
async def chat_management_flow(chat_id: int) -> str:
    """Guía: Estética de bandeja, vinculación CRM y transferencia."""
    return f"""INSTRUCCIÓN: Gestión Profesional de Chat (Openlines)
    
PASOS OBLIGATORIOS PARA EL CONTROL DE CITA:

1. **Vínculo CRM**: Usa `bitrix://openlines/session/{chat_id}/crm` para ver si ya hay un Lead. Si no lo hay, usa `manage_lead`.

2. **Email para Cita**: Antes de llamar a `calendar_event_create`, confirma que tienes el Email.

3. **Contexto de Cita**: El Título DEBE ser "[Destino] - [Nombre]" y la Descripción debe resumir lo conversado.

4. **Tarea de Seguimiento**: Tras agendar con éxito, **SIEMPRE** llama a `task_create`. 
   - **CONTENIDO**: En la descripción de la tarea, incluye la fecha/hora de la cita y el perfil del cliente (email, presupuesto, intereses). Esto es vital para el asesor.

3. **Transferencia Inteligente**: 
   - Mantén la charla mientras sea una consulta de catálogo o calificación.
   - **ANTES de transferir**: Usa `session_operator_list` para verificar si hay alguien online. Si no hay nadie, informa al cliente y ofrece tomar sus datos.
   - **Si hay operadores**: Usa `session_queue_info` para estimar el tiempo de espera y comunicárselo al cliente (ej: "Te paso con un agente, el tiempo aprox. es de X segundos").
   - **Manejo Off-Topic**: Si el cliente pregunta por temas ajenos a la agencia, intenta redirigir una vez. Al segundo intento fallido, usa `session_transfer` obligatoriamente.
   - Usa `session_transfer` también cuando el cliente pida un humano o la venta requiera negociación manual compleja.

4. **Escucha Silenciosa**: Si ya se transfirió a un humano, puedes usar `session_history_read` para leer la charla sin ser visible y generar notas internas (`crm_add_note`) con sugerencias para el equipo.

5. **Cierre**: No cierres la sesión (`session_finish`) a menos que el cliente se despida y el caso esté resuelto.
"""



@mcp.prompt()
async def internal_ops_orchestration(entity_id: int = None, entity_type: str = "LEAD") -> str:
    """Guía: Cuándo crear una Nota vs Actividad vs Tarea según el contexto."""
    return f"""INSTRUCCIÓN: Gestión de Seguimiento Interno Proactivo
    
Analiza el CONTEXTO de la conversación para decidir la herramienta:

1. **Nota (`crm_add_note`)**: Úsala cuando la información es meramente INFORMATIVA o HISTÓRICA (ej: "El cliente dice que prefiere playa"). No requiere ninguna acción futura.

2. **Actividad (`crm_activity_add`)**: Úsala para cualquier ACCIÓN CONTEXTUAL que requiera un seguimiento o respuesta (ej: "Quedamos en llamarlo", "Enviar presupuesto modificado", "Verificar disponibilidad de hotel"). 
   - Si detectas una PROMESA o COMPROMISO de tiempo en el chat, genera una Actividad.
   - Es el "pulso" comercial: llamadas, correos o tareas rápidas.

3. **Tarea (`task_create`)**: Úsala para OPERACIONES COMPLEJAS o procesos que involucren a otros departamentos (ej: "Reserva formal de grupo", "Gestión de visas", "Armado de itinerario a medida"). 

REGLA DE CONTEXTO: 
- ¿Es solo un dato? -> Nota.
- ¿Hay algo que HACER o RESPONDER pronto? -> Actividad.
- ¿Es un PROYECTO o proceso estructurado? -> Tarea.
"""

@mcp.prompt()
async def organize_drive_storage(client_name: str, entity_id: int, entity_type: str = "LEAD") -> str:
    """Guía: Resolver dominio de identidad → organizar documentos."""
    return f"""INSTRUCCIÓN: Dominio de la Identidad en Drive
    
Cliente: {client_name}
ID Entidad: {entity_id} ({entity_type})
    
REGAL DE ORO: No guardes archivos en la raíz ni en carpetas genéricas.
    
PASOS OBLIGATORIOS:
1. **Resolver Espacio**: Llama SIEMPRE a `drive_resolve_workspace` primero. Este te dará el ID de la carpeta exclusiva para este cliente.
2. **Operar**: Usa ese `workspace_id` para realizar cualquier subida (`drive_file_upload`) o creación de subcarpetas.
3. **Consulta**: Si necesitas ver qué archivos tiene este cliente, usa el recurso `bitrix://drive/folder/ID/items` con el ID del workspace resuelto.
"""

# ═══════════════════════════════════════════════════════════════════
# MAIN — Ejecutar servidor STDIO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="stdio")

@mcp.prompt()
async def advisor_transfer_strategy(chat_id: int, lead_id: int = None, advisor_id: int = None) -> str:
    """Guía: Secuencia optimizada para transferir a un asesor asegurando notificación."""
    return f"""INSTRUCCIÓN: Protocolo de Traspaso a Asesor
    
Para asegurar que el asesor sea notificado de inmediato, DEBES seguir este orden:

1. **Resumen en CRM**: Usa `crm_add_note` (entity_id={lead_id or 'ID_DEL_LEAD'}, entity_type='LEAD') con un resumen de 3 puntos de lo que el cliente busca.
2. **Transferencia**: Usa `session_transfer`(chat_id={chat_id}, user_id={advisor_id or 'ID_OPCIONAL'}).
3. **Notificación Directa (Pop-up)**: Si tienes el ID del asesor ({advisor_id or 'ID_OPCIONAL'}), usa `advisor_notify` con un mensaje breve: "[Bot] Cliente esperando en chat {chat_id}".

No omitas ningún paso para garantizar la mejor experiencia al cliente."""
