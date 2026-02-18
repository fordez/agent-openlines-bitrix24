from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List, Union

class EnrichmentFields(BaseModel):
    """
    Contenedor flexible para campos de Bitrix24.
    Permite campos estándar y campos personalizados (UF_CRM_*).
    """
    model_config = ConfigDict(extra='allow')

    # Campos comunes opcionales para ayudar al LLM (opcional)
    TITLE: Optional[str] = Field(None, description="Título del Lead o Deal")
    NAME: Optional[str] = Field(None, description="Nombre del Contacto o Lead")
    LAST_NAME: Optional[str] = Field(None, description="Apellido")
    EMAIL: Optional[Union[str, List[Dict[str, str]]]] = Field(None, description="Email del cliente")
    PHONE: Optional[Union[str, List[Dict[str, str]]]] = Field(None, description="Teléfono del cliente")
    SOURCE_ID: Optional[str] = Field(None, description="ID de origen (ej: WEB, CHAT)")
    COMMENTS: Optional[str] = Field(None, description="Comentarios internos")

class EnrichmentRequest(BaseModel):
    """Esquema para la herramienta enrich_entity."""
    entity_id: int = Field(..., description="ID de la entidad CRM")
    entity_type: str = Field(..., description="Tipo: LEAD, CONTACT, DEAL, COMPANY")
    fields: EnrichmentFields = Field(..., description="Diccionario de campos a actualizar")

# --- CRM Models ---

class ManageLeadRequest(BaseModel):
    name: Optional[str] = Field(None, description="Nombre del cliente")
    phone: Optional[str] = Field(None, description="Teléfono del cliente")
    email: Optional[str] = Field(None, description="Email del cliente")
    title: Optional[str] = Field(None, description="Título opcional para el lead")
    chat_id: Optional[int] = Field(None, description="ID del chat/sesión")
    source_id: str = Field("WEB", description="Origen (ej: WEB, CHAT)")
    comments: Optional[str] = Field(None, description="Comentarios internos")

class LeadConvertRequest(BaseModel):
    lead_id: int = Field(..., description="ID del Lead a convertir")
    deal_category_id: int = Field(0, description="Categoría del Negocio (Deal)")
    chat_id: Optional[int] = Field(None, description="ID del chat para vinculación")
    create_deal: bool = Field(True, description="¿Crear Negocio?")
    create_contact: bool = Field(True, description="¿Crear Contacto?")
    create_company: bool = Field(False, description="¿Crear Empresa?")

class DealMarkClosedRequest(BaseModel):
    deal_id: int = Field(..., description="ID del Negocio")
    status: str = Field(..., description="Estado: WON o LOST")
    comment: Optional[str] = Field(None, description="Motivo del cierre")

class CRMNoteRequest(BaseModel):
    entity_id: int = Field(..., description="ID de la entidad")
    entity_type: str = Field(..., description="Tipo: LEAD, DEAL, CONTACT, COMPANY")
    message: str = Field(..., description="Contenido de la nota")

# --- Calendar Models ---

class CalendarEventCreateRequest(BaseModel):
    title: str = Field(..., description="Título: '[Destino] - [Nombre]'")
    start_time: str = Field(..., description="Fecha/Hora de inicio (ISO 8601)")
    end_time: str = Field(..., description="Fecha/Hora de fin (ISO 8601)")
    description: str = Field("", description="Resumen de intereses/presupuesto")
    remind_mins: int = Field(60, description="Minutos para el recordatorio")
    section_id: int = Field(0, description="ID de sección de calendario")

class CalendarEventUpdateRequest(BaseModel):
    event_id: int = Field(..., description="ID del evento a modificar")
    title: Optional[str] = Field(None, description="Nuevo título")
    start_time: Optional[str] = Field(None, description="Nueva fecha inicio")
    end_time: Optional[str] = Field(None, description="Nueva fecha fin")
    description: Optional[str] = Field(None, description="Nueva descripción")
    remind_mins: Optional[int] = Field(None, description="Nuevo recordatorio")

# --- Activity / Tasks ---

class TaskCreateRequest(BaseModel):
    title: str = Field(..., description="Título de la tarea")
    description: str = Field(..., description="Detalles (Fecha cita, intereses, etc.)")
    responsible_id: Optional[int] = Field(None, description="ID del responsable")
    deadline_hours: int = Field(24, description="Plazo en horas")
    entity_id: Optional[int] = Field(None, description="ID Lead/Deal vinculado")
    entity_type: str = Field("LEAD", description="Tipo entidad CRM")

class CRMActivityAddRequest(BaseModel):
    entity_id: int = Field(..., description="ID de la entidad CRM")
    entity_type: str = Field(..., description="Tipo: LEAD o DEAL")
    subject: str = Field(..., description="Asunto de la actividad")
    type_id: int = Field(2, description="ID Tipo (2=Llamada, 1=Reunión, etc.)")
    start_time: Optional[str] = Field(None, description="Fecha inicio")
    end_time: Optional[str] = Field(None, description="Fecha fin")
    description: str = Field("", description="Detalles")

# --- Drive / Document ---

class DriveResolveWorkspaceRequest(BaseModel):
    entity_id: int = Field(..., description="ID de la entidad")
    entity_type: str = Field(..., description="Tipo entidad")
    entity_name: str = Field("Cliente", description="Nombre para la carpeta")

class DocumentGenerateRequest(BaseModel):
    template_id: int = Field(..., description="ID de la plantilla")
    entity_id: int = Field(..., description="ID de la entidad")
    entity_type_id: int = Field(2, description="ID Tipo Entidad (base Bitrix)")

# --- Openlines ---

class SessionTransferRequest(BaseModel):
    chat_id: int = Field(..., description="ID de la sesión de chat")
    user_id: Optional[int] = Field(None, description="ID del asesor específico")
    queue_id: Optional[int] = Field(1, description="ID de la cola general")

class NotifyAdvisorRequest(BaseModel):
    user_id: int = Field(..., description="ID del usuario asesor")
    message: str = Field(..., description="Mensaje de notificación")

class ChatProgressRequest(BaseModel):
    chat_id: int = Field(..., description="ID del chat de OpenLines")
    message: str = Field(..., description="Mensaje de cortesía o progreso para el cliente")

# --- Drive / Upload ---

class DriveFileUploadRequest(BaseModel):
    folder_id: int = Field(..., description="ID de la carpeta destino")
    file_name: str = Field(..., description="Nombre del archivo (ej: contrato.pdf)")
    file_content_base64: str = Field(..., description="Contenido en Base64")

# --- Catalog ---

class CatalogProductSearchRequest(BaseModel):
    name: str = Field(..., description="Nombre o palabra clave del producto")

class CatalogProductListRequest(BaseModel):
    section_id: int = Field(..., description="ID de la sección/categoría")

class DealAddProductsRequest(BaseModel):
    deal_id: int = Field(..., description="ID del Negocio")
    products: List[Dict[str, Any]] = Field(..., description="Lista de {'PRODUCT_ID': id, 'PRICE': val, 'QUANTITY': val}")


