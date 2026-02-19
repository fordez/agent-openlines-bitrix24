"""
Herramientas de Bitrix24 integradas directamente en el proceso principal.
Elimina la necesidad de servidores MCP externos y subprocesos pesados.
"""
import sys
import os
import asyncio
from typing import Dict, Any, Optional, List, Union
from app.models import (
    CRMNoteRequest, CalendarEventCreateRequest,
    CalendarEventUpdateRequest, TaskCreateRequest, CRMActivityAddRequest,
    DriveResolveWorkspaceRequest, DocumentGenerateRequest, SessionTransferRequest,
    DriveFileUploadRequest, CatalogProductSearchRequest, CatalogProductListRequest,
    DealAddProductsRequest, NotifyAdvisorRequest, ChatProgressRequest,
    ManageLeadRequest, LeadConvertRequest, EnrichmentFields
)
from app.context_vars import member_id_var

# --- Utility para establecer contexto ---
async def _set_context(chat_id: Optional[Union[int, str]] = None):
    if chat_id:
        from app.token_manager import get_token_manager
        tm = await get_token_manager()
        m_id = await tm.get_member_id_from_chat(str(chat_id))
        if m_id:
            member_id_var.set(m_id)
            os.environ["BITRIX_MEMBER_ID"] = m_id

# --- CRM / Leads ---
async def manage_lead(name: str = None, phone: str = None, email: str = None, **kwargs) -> str:
    from tools.crm.manage_lead import manage_lead as _fn
    chat_id = kwargs.get('chat_id')
    await _set_context(chat_id)
    return await _fn(name=name, phone=phone, email=email, **kwargs)

async def lead_get(lead_id: int) -> str:
    from tools.crm.lead_get import lead_get as _fn
    return await _fn(lead_id=lead_id)

async def lead_convert(lead_id: int, **kwargs) -> str:
    from tools.crm.lead_convert import lead_convert as _fn
    await _set_context(kwargs.get('chat_id'))
    return await _fn(lead_id=lead_id, **kwargs)

# --- Openlines ---
async def chat_send_progress(chat_id: int, message: str) -> str:
    from tools.openlines.chat_send_progress import chat_send_progress as _fn
    await _set_context(chat_id)
    return await _fn(chat_id=chat_id, message=message)

async def session_transfer(chat_id: int, **kwargs) -> str:
    from tools.openlines.session_transfer import session_transfer as _fn
    await _set_context(chat_id)
    return await _fn(chat_id=chat_id, **kwargs)

async def session_crm_get(chat_id: int) -> str:
    from tools.openlines.session_crm_get import session_crm_get as _fn
    await _set_context(chat_id)
    return await _fn(chat_id=chat_id)

# --- Calendar ---
async def calendar_availability_check(start_time: str, end_time: str) -> str:
    from tools.calendar.calendar_availability_check import calendar_availability_check as _fn
    return await _fn(start_time=start_time, end_time=end_time)

async def calendar_event_create(title: str, start_time: str, end_time: str, **kwargs) -> str:
    from tools.calendar.calendar_event_create import calendar_event_create as _fn
    return await _fn(title=title, start_time=start_time, end_time=end_time, **kwargs)

# Diccionario de mapeo para registro dinámico
BITRIX_TOOLS = {
    "manage_lead": manage_lead,
    "lead_get": lead_get,
    "lead_convert": lead_convert,
    "chat_send_progress": chat_send_progress,
    "session_transfer": session_transfer,
    "session_crm_get": session_crm_get,
    "calendar_availability_check": calendar_availability_check,
    "calendar_event_create": calendar_event_create,
}
