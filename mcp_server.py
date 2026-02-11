"""
MCP Server Local (STDIO) para Bot Viajes — Bitrix24 CRM.
Expone todas las tools existentes como MCP Tools, recursos de solo-lectura
como Resources, y plantillas de orquestación como Prompts.

Uso: python mcp_server.py  (se comunica por STDIO con mcp-agent)
"""
import sys
import os
from dotenv import load_dotenv

# Asegurar que el directorio raíz esté en el path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

# Cargar variables de entorno desde el path absoluto
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

# Debug logs para el subproceso
sys.stderr.write(f"🔧 MCP Server BaseDir: {base_dir}\n")
sys.stderr.write(f"🔧 MCP Server .env path: {dotenv_path}\n")
sys.stderr.write(f"🔧 MCP Server REDIS_URL: {os.getenv('REDIS_URL')}\n")
sys.stderr.write(f"🔧 MCP Server BITRIX_DOMAIN: {os.getenv('BITRIX_DOMAIN')}\n")

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
async def manage_lead(name: str = None, phone: str = None, email: str = None, title: str = None, chat_id: int = None, source_id: str = "WEB", comments: str = None) -> str:
    """Usa esta tool PRINCIPAL para GESTIONAR LEADS. 
    Es INTELIGENTE: Busca duplicados por teléfono/email. Si existe, lo actualiza. Si no, crea uno nuevo.
    Siempre úsala cuando tengas datos del cliente."""
    try:
        from tools.crm.manage_lead import manage_lead as _fn
        return await _fn(name=name, phone=phone, email=email, title=title, chat_id=chat_id, source_id=source_id, comments=comments)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en manage_lead: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en manage_lead: {e}"

@mcp.tool()
async def crm_add_note(entity_id: int, entity_type: str, message: str) -> str:
    """Usa esta tool para AGREGAR UNA NOTA o comentario (ej: intereses, score, resumen) a cualquier Lead, Contacto o Negocio en el CRM."""
    try:
        from tools.crm.crm_add_note import crm_add_note as _fn
        return await _fn(entity_id=entity_id, entity_type=entity_type, message=message)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en crm_add_note: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en crm_add_note: {e}"



@mcp.tool()
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
async def lead_convert(lead_id: int, deal_category_id: int = 0, chat_id: int = None, create_company: bool = False) -> str:
    """CONVIERTE un Lead en Deal + Contacto (B2C) o Contacto + Empresa (B2B). 
    Úsalo como señal de avance (ej: al agendar cita). create_company=True para B2B."""
    try:
        from tools.crm.lead_convert import lead_convert as _fn
        return await _fn(lead_id=lead_id, deal_category_id=deal_category_id, chat_id=chat_id, create_company=create_company)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_convert: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_convert: {e}"

@mcp.tool()
async def enrich_entity(entity_id: int, entity_type: str, fields: dict) -> str:
    """Usa esta tool para ENRIQUECER cualquier entidad (LEAD, CONTACT, DEAL) con datos inteligentes 
    como origen del canal, comentarios detallados o campos personalizados una vez creada la ficha."""
    try:
        from tools.crm.enrich_entity import enrich_entity as _fn
        return await _fn(entity_id=entity_id, entity_type=entity_type, fields=fields)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en enrich_entity: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en enrich_entity: {e}"


# ─── CRM / Contacts ──────────────────────────────────────────────

@mcp.tool()
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
async def deal_mark_closed(deal_id: int, status: str, comment: str = None) -> str:
    """Usa esta tool para CERRAR el negocio. status='WON' para Ganado, status='LOST' para Perdido. Puedes añadir un motivo en comment."""
    try:
        from tools.deal.deal_mark_closed import deal_mark_closed as _fn
        return await _fn(deal_id=deal_id, status=status, comment=comment)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_mark_closed: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_mark_closed: {e}"

@mcp.tool()
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
async def calendar_event_list(from_date: str = None, to_date: str = None) -> str:
    """Usa esta tool para LEER LA AGENDA y saber qué reuniones hay programadas en un rango."""
    from tools.calendar.calendar_event_list import calendar_event_list as _fn
    return await _fn(from_date=from_date, to_date=to_date)

@mcp.tool()
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
async def calendar_event_create(title: str, start_time: str, end_time: str, description: str = "", remind_mins: int = 60) -> str:
    """Usa esta tool para AGENDAR una cita. Proporciona remind_mins para configurar recordatorio automático."""
    try:
        from tools.calendar.calendar_event_create import calendar_event_create as _fn
        return await _fn(title=title, start_time=start_time, end_time=end_time, description=description, remind_mins=remind_mins)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_create: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_create: {e}"

@mcp.tool()
async def calendar_event_update(event_id: int, title: str = None, start_time: str = None, end_time: str = None, description: str = None, remind_mins: int = None) -> str:
    """Usa esta tool para MODIFICAR o REPROGRAMAR una reunión existente."""
    try:
        from tools.calendar.calendar_event_update import calendar_event_update as _fn
        return await _fn(event_id=event_id, title=title, start_time=start_time, end_time=end_time, description=description, remind_mins=remind_mins)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en calendar_event_update: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en calendar_event_update: {e}"

@mcp.tool()
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
async def catalog_product_list(section_id: int) -> str:
    """Usa esta tool para LISTAR PRODUCTOS dentro de una categoría/sección específica."""
    try:
        from tools.catalog.catalog_product_list import catalog_product_list as _fn
        return await _fn(section_id=section_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en catalog_product_list: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en catalog_product_list: {e}"

@mcp.tool()
async def catalog_product_get(product_id: int) -> str:
    """Usa esta tool para ver DETALLES COMPLETOS de un producto específico por ID."""
    from tools.catalog.catalog_product_get import catalog_product_get as _fn
    return await _fn(product_id=product_id)

@mcp.tool()
async def catalog_product_search(name: str) -> str:
    """Usa esta tool para BUSCAR PRODUCTOS por nombre o palabra clave."""
    try:
        from tools.catalog.catalog_product_search import catalog_product_search as _fn
        return await _fn(name=name)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en catalog_product_search: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en catalog_product_search: {e}"

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
    try:
        from tools.followup.lead_reactivate_by_client import lead_reactivate_by_client as _fn
        return await _fn(lead_id=lead_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en lead_reactivate_by_client: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en lead_reactivate_by_client: {e}"

@mcp.tool()
async def deal_update_probability_client(deal_id: int, probability: int) -> str:
    """Usa esta tool para ACTUALIZAR la probabilidad de cierre de un Deal (0-100)."""
    try:
        from tools.followup.deal_update_probability_client import deal_update_probability_client as _fn
        return await _fn(deal_id=deal_id, probability=probability)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en deal_update_probability_client: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en deal_update_probability_client: {e}"

# ─── Openlines ────────────────────────────────────────────────────


@mcp.tool()
async def session_transfer(chat_id: int, user_id: int = None) -> str:
    """Usa esta tool para TRANSFERIR la conversación a un HUMANO cuando la situación se complique."""
    try:
        from tools.openlines.session_transfer import session_transfer as _fn
        return await _fn(chat_id=chat_id, user_id=user_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_transfer: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_transfer: {e}"

@mcp.tool()
async def session_finish(chat_id: int) -> str:
    """Usa esta tool para CERRAR la sesión de chat cuando la conversación haya terminado."""
    from tools.openlines.session_finish import session_finish as _fn
    return await _fn(chat_id=chat_id)

@mcp.tool()
async def session_title_update(chat_id: int, title: str) -> str:
    """Usa esta tool para ACTUALIZAR EL TÍTULO de la conversación en Bitrix24. Hazlo en cuanto identifiques el tema del viaje (ej: 'Planificación China') para que no aparezca como 'sin title'."""
    try:
        from tools.openlines.session_title_update import session_title_update as _fn
        return await _fn(chat_id=chat_id, title=title)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_title_update: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_title_update: {e}"


@mcp.tool()
async def session_crm_get(chat_id: int) -> str:
    """Usa esta tool para VERIFICAR si ya existe un Lead vinculado a la sesión actual ANTES de crear uno nuevo."""
    try:
        from tools.openlines.session_crm_get import session_crm_get as _fn
        return await _fn(chat_id=chat_id)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_crm_get: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_crm_get: {e}"

@mcp.tool()
async def session_crm_bind(chat_id: int, entity_id: int, entity_type: str = "LEAD") -> str:
    """Usa esta tool DESPUÉS de crear un Lead para VINCULARLO explícitamente a la sesión de chat actual. REQUIERE entity_id."""
    try:
        from tools.openlines.session_crm_bind import session_crm_bind as _fn
        return await _fn(chat_id=chat_id, entity_id=entity_id, entity_type=entity_type)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en session_crm_bind: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en session_crm_bind: {e}"

# ─── Activity / Tasks (Observer) ─────────────────────────────────

@mcp.tool()
async def task_create(title: str, description: str, responsible_id: int = None, deadline_hours: int = 24, entity_id: int = None, entity_type: str = "LEAD") -> str:
    """Usa esta tool para CREAR TAREAS de seguimiento interno. Puede vincularse a un Lead o Deal."""
    try:
        from tools.task.task_create import task_create as _fn
        return await _fn(title=title, description=description, responsible_id=responsible_id, deadline_hours=deadline_hours, entity_id=entity_id, entity_type=entity_type)
    except Exception as e:
        import traceback
        sys.stderr.write(f"  ❌ Error en task_create: {e}\n{traceback.format_exc()}\n")
        return f"Error técnico en task_create: {e}"

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


# ═══════════════════════════════════════════════════════════════════
# PROMPTS — Plantillas de orquestación para guiar al agente
# ═══════════════════════════════════════════════════════════════════

@mcp.prompt()
async def identity_management_strategy(chat_id: int, name: str = "", phone: str = "", email: str = "") -> str:
    """Guía: Prioridad de aceptación, actualización de datos y disparador de Lead."""
    return f"""INSTRUCCIÓN: Gestión de Sesión, Identidad y Prospectos
    
Sigue esta jerarquía obligatoria para gestionar al cliente:
    
1. **Estética de Bandeja (Título)**: En cuanto identifiques el tema o país de interés, usa `session_title_update`. Esto es vital para que el chat tenga un nombre claro en la bandeja de Bitrix.

2. **DISPARADOR DE LEAD (¡CRITICAL!)**: Si el cliente ya dio su **NOMBRE** y/o **TELÉFONO** ({name or 'Desconocido'}, {phone or 'Desconocido'}) y NO hay un Lead vinculado:
    - **Debes llamar a `manage_lead` de inmediato**.
    - **IMPORTANTE**: Asegúrate de pasar el `name` y el `phone` como argumentos a `manage_lead`. Esto evitará duplicados y creará o actualizará el registro según corresponda.
    - Esto garantiza que el cliente aparezca en la sección de **Prospectos** (Leads) de Bitrix24.
    
3. **ACTUALIZACIÓN DE DATOS**: Si el cliente da un nuevo dato (ej: su teléfono que antes no tenías, o corrige su nombre), usa `manage_lead` nuevamente con los nuevos datos.
    
4. **ENRIQUECIMIENTO**: Una vez asegurado el Lead, usa `enrich_entity` para completar detalles complejos si es necesario.
    
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
1. Usa `calendar_availability_check` para el rango de fechas solicitado.
2. **SI EL CLIENTE ES UN LEAD**: Ejecuta `lead_convert` para crear el Negocio (Deal) ANTES de agendar.
3. Con el DEAL_ID (o el ID de la entidad CRM), usa `calendar_event_create` para agendar.
4. Confirma la cita al cliente resaltando que ya está en agenda.

NOTA: La tool `calendar_event_create` ya incluye el recordatorio de 60 min por defecto."""


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
1. Usa `lead_add` proporcionando el `chat_id` ({chat_id}).
2. El sistema creará el Lead y lo VINCULARÁ automáticamente a esta conversación.
3. Esto permite que el historial del chat sea visible para los vendedores dentro de la ficha del Lead.
4. Una vez creado, puedes informar al cliente que un asesor revisará su solicitud.
"""


@mcp.prompt()
async def check_and_bind_crm(chat_id: int, lead_id: int = None) -> str:
    """Guía: Verificar si el chat ya tiene CRM y vincular un Lead si es necesario."""
    return f"""INSTRUCCIÓN: Gestión de CRM en Chat
    
PASOS:
1. Usa `session_crm_get` para ver si el chat ({chat_id}) ya tiene un Lead o Deal.
2. Si NO hay nada vinculado y acabas de crear un Lead ({lead_id or 'ID_NUEVO'}), usa `session_crm_bind`.
3. Esto asegura que la conversación aparezca dentro de la ficha del Lead en Bitrix24.
"""

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
   - Actualizar info → `deal_update_info`
   - Mover etapa → `deal_move_stage`
   - Agregar productos → `catalog_product_search` → `deal_add_products`
   - Cerrar → `deal_mark_closed`
   - Agregar nota → `crm_add_note` (entity_type='DEAL')
3. Registra siempre un resumen de la gestión con `crm_add_note`.

NOTA: Siempre verificar el estado actual antes de hacer cambios."""


@mcp.prompt()
async def conversion_strategy(lead_id: int, chat_id: int = None, is_b2b: bool = False) -> str:
    """Guía: Cuándo y cómo realizar la conversión de Lead a Deal."""
    return f"""INSTRUCCIÓN: El Salto a Negocio (Conversion)
    
La SEÑAL para convertir es el AGENDAMIENTO de una cita o una petición formal de cotización.
    
PASOS:
1. Determina si es B2C (Individuo) o B2B (Empresa).
2. Ejecuta `lead_convert` con lead_id={lead_id}, chat_id={chat_id} and create_company={is_b2b}.
3. Recibirás un DEAL_ID y un CONTACTO_ID (y opcionalmente COMPANY_ID).
4. Usa el DEAL_ID para crear el evento en el calendario.
5. Esto asegura que el "vendedor" vea la cita atada al Negocio real.
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
    
Usa `crm_add_note` para dejar constancia de cualquier detalle relevante que no encaje en un campo estándar (ej: preferencias de viaje, presupuesto mencionado, score de interés).
    
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
2. **Añadir**: Usa `deal_add_products` para vincular ese producto al Deal ({deal_id}).
3. **Plantilla**: Usa `document_template_list` para ver qué plantillas de cotización hay disponibles (entity_type_id=2).
4. **Generar**: Usa `document_generate` con el `template_id` elegido y el `entity_id`={deal_id}.
5. **Entregar**: Usa `document_download` para darle los links de PDF/Word al cliente.
6. **Nota**: Registra el envío de la cotización con `crm_add_note`.
"""

@mcp.prompt()
async def internal_ops_orchestration(entity_id: int = None, entity_type: str = "LEAD") -> str:
    """Guía: Cuándo crear una Nota vs una Tarea interna."""
    return f"""INSTRUCCIÓN: Gestión de Seguimiento (Nota vs Tarea)
    
PASOS PARA DECIDIR:
1. **Nota (`crm_add_note`)**: Úsala para REGISTRAR INTERACCIONES. Es HISTORIAL.
2. **Tarea (`task_create`)**: Úsala para ACCIONES PENDIENTES. Es TRABAJO POR HACER con un responsable.
3. **Regla de Oro**: Si requiere un responsable y un plazo (Deadline), es una Tarea. Si es solo información, es una Nota.
"""

# ═══════════════════════════════════════════════════════════════════
# MAIN — Ejecutar servidor STDIO
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run(transport="stdio")
