"""
MCP Server Local (STDIO) para Bot Viajes — Bitrix24 CRM.
Expone todas las tools existentes como MCP Tools, recursos de solo-lectura
como Resources, y plantillas de orquestación como Prompts.

Uso: python mcp_server.py  (se comunica por STDIO con mcp-agent)
"""
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

# ─── Inicializar servidor ─────────────────────────────────────────
mcp = FastMCP(
    name="bitrix_crm",
)

# ═══════════════════════════════════════════════════════════════════
# TOOLS — Funciones de acción que modifican o consultan Bitrix24
# ═══════════════════════════════════════════════════════════════════

# ─── CRM / Leads ──────────────────────────────────────────────────

@mcp.tool()
async def enrich_identity(name: str = None, phone: str = None, email: str = None) -> str:
    """Usa esta tool al INICIO para buscar si el contacto ya existe en la base de datos (Leads/Contactos). Ayuda a retomar conversaciones pasadas."""
    from tools.crm.enrich_identity import enrich_identity as _fn
    return await _fn(name=name, phone=phone, email=email)

@mcp.tool()
async def qualify_lead(entity_id: str, intention: str, score: int, next_action: str) -> str:
    """Usa esta tool para REGISTRAR la calificación de un Lead/Contacto (Intención, Score, Siguiente paso)."""
    from tools.crm.qualify_lead import qualify_lead as _fn
    return await _fn(entity_id=entity_id, intention=intention, score=score, next_action=next_action)

@mcp.tool()
async def find_duplicate(phone: str = None, email: str = None) -> str:
    """Usa esta tool para EVITAR DUPLICADOS verificando si ya existe un Lead/Contacto con ese teléfono/email. Usa esto antes de crear un Lead nuevo."""
    from tools.crm.find_duplicate import find_duplicate as _fn
    return await _fn(phone=phone, email=email)

@mcp.tool()
async def lead_add(title: str, name: str = None, last_name: str = None, phone: str = None, email: str = None, source_id: str = "WEB") -> str:
    """Usa esta tool para CREAR un nuevo Lead cuando identifiques un cliente potencial nuevo que no existe."""
    from tools.crm.lead_add import lead_add as _fn
    return await _fn(title=title, name=name, last_name=last_name, phone=phone, email=email, source_id=source_id)

@mcp.tool()
async def lead_update(lead_id: int, fields: dict) -> str:
    """Usa esta tool para ACTUALIZAR datos de un Lead existente (ej: agregar teléfono, corregir nombre)."""
    from tools.crm.lead_update import lead_update as _fn
    return await _fn(lead_id=lead_id, fields=fields)

@mcp.tool()
async def lead_convert(lead_id: int, deal_category_id: int = 0) -> str:
    """Usa esta tool para CONVERTIR un Lead en Deal + Contacto cuando el cliente muestra interés real de compra."""
    from tools.crm.lead_convert import lead_convert as _fn
    return await _fn(lead_id=lead_id, deal_category_id=deal_category_id)

# ─── Deals ────────────────────────────────────────────────────────

@mcp.tool()
async def deal_get(deal_id: int) -> str:
    """Usa esta tool para LEER toda la información detallada de un Deal específico (Monto, etapa, cliente asignado, etc)."""
    from tools.deal.deal_get import deal_get as _fn
    return await _fn(deal_id=deal_id)

@mcp.tool()
async def deal_list(filter_status: str = None, limit: int = 10) -> str:
    """Usa esta tool para LISTAR Deals activos, filtrados por etapa si es necesario."""
    from tools.deal.deal_list import deal_list as _fn
    return await _fn(filter_status=filter_status, limit=limit)

@mcp.tool()
async def deal_update_info(deal_id: int, title: str = None, opportunity: float = None) -> str:
    """Usa esta tool para ACTUALIZAR datos básicos del Deal (Título o Monto)."""
    from tools.deal.deal_update_info import deal_update_info as _fn
    return await _fn(deal_id=deal_id, title=title, opportunity=opportunity)

@mcp.tool()
async def deal_move_stage(deal_id: int, stage_id: str) -> str:
    """Usa esta tool para MOVER el Deal a una nueva etapa (ej: de 'Nuevo' a 'Cotización Enviada')."""
    from tools.deal.deal_move_stage import deal_move_stage as _fn
    return await _fn(deal_id=deal_id, stage_id=stage_id)

@mcp.tool()
async def deal_mark_closed(deal_id: int, won: bool = True) -> str:
    """Usa esta tool para CERRAR el negocio. won=True si el cliente compró (Ganado), won=False si se perdió."""
    from tools.deal.deal_mark_closed import deal_mark_closed as _fn
    return await _fn(deal_id=deal_id, won=won)

@mcp.tool()
async def deal_add_note(deal_id: int, note: str) -> str:
    """Usa esta tool para AGREGAR UNA NOTA rápida al Deal."""
    from tools.deal.deal_add_note import deal_add_note as _fn
    return await _fn(deal_id=deal_id, note=note)

# ─── Calendar ─────────────────────────────────────────────────────

@mcp.tool()
async def calendar_event_list(from_date: str = None, to_date: str = None) -> str:
    """Usa esta tool para LEER LA AGENDA y saber qué reuniones hay programadas en un rango."""
    from tools.calendar.calendar_event_list import calendar_event_list as _fn
    return await _fn(from_date=from_date, to_date=to_date)

@mcp.tool()
async def calendar_availability_check(start_time: str, end_time: str) -> str:
    """Usa esta tool para VERIFICAR DISPONIBILIDAD antes de agendar. Retorna si el horario está libre u ocupado."""
    from tools.calendar.calendar_availability_check import calendar_availability_check as _fn
    return await _fn(start_time=start_time, end_time=end_time)

@mcp.tool()
async def calendar_event_create(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """Usa esta tool para AGENDAR una cita/reunión en el calendario del agente. Útil cuando el cliente confirma disponibilidad."""
    from tools.calendar.calendar_event_create import calendar_event_create as _fn
    return await _fn(title=title, start_time=start_time, end_time=end_time, description=description)

@mcp.tool()
async def calendar_event_update(event_id: int, title: str = None, description: str = None) -> str:
    """Usa esta tool para MODIFICAR una reunión existente (ej: cambiar título o notas)."""
    from tools.calendar.calendar_event_update import calendar_event_update as _fn
    return await _fn(event_id=event_id, title=title, description=description)

@mcp.tool()
async def calendar_event_delete(event_id: int) -> str:
    """Usa esta tool para CANCELAR/BORRAR una reunión."""
    from tools.calendar.calendar_event_delete import calendar_event_delete as _fn
    return await _fn(event_id=event_id)

@mcp.tool()
async def calendar_event_set_reminder(event_id: str, minutes: int = 60, owner_id: int = 1) -> str:
    """Usa esta tool para CONFIGURAR RECORDATORIO automático antes del evento."""
    from tools.calendar.calendar_event_set_reminder import calendar_event_set_reminder as _fn
    return await _fn(event_id=event_id, minutes=minutes, owner_id=owner_id)

# ─── Catalog / Products ──────────────────────────────────────────

@mcp.tool()
async def catalog_product_list(catalog_id: int, section_id: int = None) -> str:
    """Usa esta tool para LISTAR PRODUCTOS de un catálogo, opcionalmente filtrados por sección/categoría."""
    from tools.catalog.catalog_product_list import catalog_product_list as _fn
    return await _fn(catalog_id=catalog_id, section_id=section_id)

@mcp.tool()
async def catalog_product_get(product_id: int) -> str:
    """Usa esta tool para ver DETALLES COMPLETOS de un producto específico por ID."""
    from tools.catalog.catalog_product_get import catalog_product_get as _fn
    return await _fn(product_id=product_id)

@mcp.tool()
async def catalog_product_search(query: str) -> str:
    """Usa esta tool para BUSCAR PRODUCTOS por nombre o palabra clave."""
    from tools.catalog.catalog_product_search import catalog_product_search as _fn
    return await _fn(query=query)

@mcp.tool()
async def deal_add_products(deal_id: int, products: list) -> str:
    """Usa esta tool para AGREGAR PRODUCTOS a un Deal existente."""
    from tools.catalog.deal_add_products import deal_add_products as _fn
    return await _fn(deal_id=deal_id, products=products)

@mcp.tool()
async def deal_update_products(row_id: int, fields: dict) -> str:
    """Usa esta tool para MODIFICAR un producto ya agregado en un Deal (cantidad, precio)."""
    from tools.catalog.deal_update_products import deal_update_products as _fn
    return await _fn(row_id=row_id, fields=fields)

@mcp.tool()
async def deal_remove_product(row_id: int) -> str:
    """Usa esta tool para ELIMINAR un producto de un Deal."""
    from tools.catalog.deal_remove_product import deal_remove_product as _fn
    return await _fn(row_id=row_id)

# ─── Document ─────────────────────────────────────────────────────

@mcp.tool()
async def document_generate(template_id: int, entity_id: int, entity_type_id: int = 2) -> str:
    """Usa esta tool para GENERAR un documento (contrato, cotización) basado en una plantilla y una entidad CRM."""
    from tools.document.document_generate import document_generate as _fn
    return await _fn(template_id=template_id, entity_id=entity_id, entity_type_id=entity_type_id)

@mcp.tool()
async def document_list(entity_id: int, entity_type_id: int = 2) -> str:
    """Usa esta tool para VER qué documentos ya fueron generados para un Lead o Deal."""
    from tools.document.document_list import document_list as _fn
    return await _fn(entity_id=entity_id, entity_type_id=entity_type_id)

@mcp.tool()
async def document_download(document_id: int) -> str:
    """Usa esta tool para DESCARGAR un documento ya generado y obtener su URL."""
    from tools.document.document_download import document_download as _fn
    return await _fn(document_id=document_id)

# ─── Drive ────────────────────────────────────────────────────────

@mcp.tool()
async def drive_folder_create(name: str, parent_id: int = None) -> str:
    """Usa esta tool para CREAR una nueva carpeta en Bitrix24 Drive."""
    from tools.drive.drive_folder_create import drive_folder_create as _fn
    return await _fn(name=name, parent_id=parent_id)

@mcp.tool()
async def drive_file_upload(folder_id: int, file_name: str, file_content_base64: str) -> str:
    """Usa esta tool para SUBIR un archivo al Drive de Bitrix24."""
    from tools.drive.drive_file_upload import drive_file_upload as _fn
    return await _fn(folder_id=folder_id, file_name=file_name, file_content_base64=file_content_base64)

@mcp.tool()
async def drive_file_list(folder_id: int) -> str:
    """Usa esta tool para VER los archivos dentro de una carpeta del Drive."""
    from tools.drive.drive_file_list import drive_file_list as _fn
    return await _fn(folder_id=folder_id)

@mcp.tool()
async def drive_file_download(file_id: int) -> str:
    """Usa esta tool para DESCARGAR un archivo del Drive y obtener su URL."""
    from tools.drive.drive_file_download import drive_file_download as _fn
    return await _fn(file_id=file_id)

# ─── Followup ─────────────────────────────────────────────────────

@mcp.tool()
async def lead_reactivate_by_client(lead_id: int) -> str:
    """Usa esta tool cuando un cliente con Lead anterior vuelve a escribir. Reactiva el Lead cambiando su STATUS_ID."""
    from tools.followup.lead_reactivate_by_client import lead_reactivate_by_client as _fn
    return await _fn(lead_id=lead_id)

@mcp.tool()
async def deal_detect_stage_for_client(deal_id: int) -> str:
    """Usa esta tool para DETECTAR la etapa actual de un Deal y reportarla."""
    from tools.followup.deal_detect_stage_for_client import deal_detect_stage_for_client as _fn
    return await _fn(deal_id=deal_id)

@mcp.tool()
async def deal_add_client_objection(deal_id: int, objection: str) -> str:
    """Usa esta tool cuando el cliente expresa una OBJECIÓN en la conversación. La registra en el Deal."""
    from tools.followup.deal_add_client_objection import deal_add_client_objection as _fn
    return await _fn(deal_id=deal_id, objection=objection)

@mcp.tool()
async def deal_update_probability_client(deal_id: int, probability: int) -> str:
    """Usa esta tool para ACTUALIZAR la probabilidad de cierre de un Deal."""
    from tools.followup.deal_update_probability_client import deal_update_probability_client as _fn
    return await _fn(deal_id=deal_id, probability=probability)

@mcp.tool()
async def lead_next_action_client(lead_id: int, action_description: str) -> str:
    """Usa esta tool para REGISTRAR la siguiente acción a tomar en un Lead."""
    from tools.followup.lead_next_action_client import lead_next_action_client as _fn
    return await _fn(lead_id=lead_id, action_description=action_description)

@mcp.tool()
async def deal_next_action_client(deal_id: int, action_description: str) -> str:
    """Usa esta tool para REGISTRAR la siguiente acción a tomar en un Deal."""
    from tools.followup.deal_next_action_client import deal_next_action_client as _fn
    return await _fn(deal_id=deal_id, action_description=action_description)

@mcp.tool()
async def deal_follow_up_schedule_client(deal_id: int, follow_up_date: str, note: str) -> str:
    """Usa esta tool para PROGRAMAR un seguimiento futuro en un Deal."""
    from tools.followup.deal_follow_up_schedule_client import deal_follow_up_schedule_client as _fn
    return await _fn(deal_id=deal_id, follow_up_date=follow_up_date, note=note)

@mcp.tool()
async def lead_follow_up_note_client(lead_id: int, note: str) -> str:
    """Usa esta tool para dejar una NOTA de seguimiento en un Lead."""
    from tools.followup.lead_follow_up_note_client import lead_follow_up_note_client as _fn
    return await _fn(lead_id=lead_id, note=note)

# ─── Openlines ────────────────────────────────────────────────────

@mcp.tool()
async def session_send_message(chat_id: int, message: str) -> str:
    """Usa esta tool para ENVIAR MENSAJES al cliente por el canal abierto (WhatsApp/Web)."""
    from tools.openlines.session_send_message import session_send_message as _fn
    return await _fn(chat_id=chat_id, message=message)

@mcp.tool()
async def session_transfer(chat_id: int, user_id: int = None) -> str:
    """Usa esta tool para TRANSFERIR la conversación a un HUMANO cuando la situación se complique."""
    from tools.openlines.session_transfer import session_transfer as _fn
    return await _fn(chat_id=chat_id, user_id=user_id)

@mcp.tool()
async def session_finish(chat_id: int) -> str:
    """Usa esta tool para CERRAR la sesión de chat cuando la conversación haya terminado."""
    from tools.openlines.session_finish import session_finish as _fn
    return await _fn(chat_id=chat_id)

@mcp.tool()
async def crm_chat_link(chat_id: int, entity_id: int, entity_type: str = "DEAL") -> str:
    """Usa esta tool para VINCULAR el chat actual a un Deal o Lead del CRM."""
    from tools.openlines.crm_chat_link import crm_chat_link as _fn
    return await _fn(chat_id=chat_id, entity_id=entity_id, entity_type=entity_type)

# ─── Activity / Tasks (Observer) ─────────────────────────────────

@mcp.tool()
async def activity_add(activity_type: str, subject: str, description: str, owner_id: str = None, owner_type_id: int = 1) -> str:
    """Usa esta tool para REGISTRAR actividades/notas de seguimiento en el CRM (Leads/Deals/Contacts)."""
    from tools.activity.activity_add import activity_add as _fn
    return await _fn(activity_type=activity_type, subject=subject, description=description, owner_id=owner_id, owner_type_id=owner_type_id)

@mcp.tool()
async def task_create(title: str, description: str, responsible_id: int = None, deadline_hours: int = 24) -> str:
    """Usa esta tool para CREAR TAREAS para que un humano continúe acciones necesarias."""
    from tools.task.task_create import task_create as _fn
    return await _fn(title=title, description=description, responsible_id=responsible_id, deadline_hours=deadline_hours)


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

@mcp.resource("bitrix://drive/folders")
async def resource_drive_folders() -> str:
    """Carpetas raíz del Drive de Bitrix24."""
    from tools.drive.drive_folder_list import drive_folder_list as _fn
    return await _fn()


# ═══════════════════════════════════════════════════════════════════
# PROMPTS — Plantillas de orquestación para guiar al agente
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
async def qualify_and_assign(client_name: str = "", client_phone: str = "", client_email: str = "") -> str:
    """Guía de orquestación: Identificar cliente → buscar duplicados → calificar → crear o actualizar Lead."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Calificar y Asignar Lead

Datos del cliente:
- Nombre: {client_name or 'No proporcionado'}
- Teléfono: {client_phone or 'No proporcionado'}
- Email: {client_email or 'No proporcionado'}

PASOS A SEGUIR:
1. Usa enrich_identity con los datos disponibles para buscar si ya existe.
2. Si hay coincidencias, verifica el estado del Lead/Deal existente.
3. Si NO hay coincidencias, usa find_duplicate para confirmar que no es duplicado.
4. Si es un cliente nuevo, usa lead_add para crear el Lead.
5. Usa qualify_lead para registrar la calificación basada en la conversación.
6. Si el cliente muestra interés real, considera usar lead_convert.

IMPORTANTE: No crear duplicados. Siempre verificar primero."""


@mcp.prompt()
async def schedule_meeting(client_name: str = "", preferred_date: str = "", meeting_type: str = "virtual") -> str:
    """Guía de orquestación: Verificar disponibilidad → ofrecer opciones → agendar → confirmar."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Agendar Reunión

Cliente: {client_name or 'Desconocido'}
Fecha preferida: {preferred_date or 'Flexible'}
Tipo: {meeting_type}

PASOS A SEGUIR:
1. Usa calendar_availability_check para el rango de fechas solicitado.
2. Si hay disponibilidad, ofrece 3 opciones de horario al cliente.
3. Cuando el cliente confirme, usa calendar_event_create con título descriptivo.
4. Usa calendar_event_set_reminder para configurar recordatorio (60 min antes).
5. Confirma la cita al cliente con todos los detalles.

NOTA: Si es virtual, mencionar que recibirá link de Teams."""


@mcp.prompt()
async def manage_deal(deal_id: str = "", action: str = "") -> str:
    """Guía de orquestación: Obtener deal → actualizar info → mover etapa → agregar productos."""
    return f"""INSTRUCCIÓN DE ORQUESTACIÓN — Gestionar Deal

Deal ID: {deal_id or 'Por determinar'}
Acción solicitada: {action or 'Revisar estado'}

PASOS A SEGUIR:
1. Usa deal_get para obtener información completa del Deal.
2. Según la acción:
   - Actualizar info → deal_update_info
   - Mover etapa → deal_move_stage
   - Agregar productos → catalog_product_search → deal_add_products
   - Cerrar → deal_mark_closed
   - Agregar nota → deal_add_note
3. Registra la acción realizada con deal_add_note.

NOTA: Siempre verificar el estado actual antes de hacer cambios."""


# ═══════════════════════════════════════════════════════════════════
# MAIN — Ejecutar servidor STDIO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="stdio")
