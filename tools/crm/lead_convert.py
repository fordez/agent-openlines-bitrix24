"""
Herramienta para convertir un Lead en Contacto + Deal en Bitrix24.
Usa crm.lead.update y luego crea Contacto/Deal manualmente.
"""
from app.auth import call_bitrix_method
import json

def lead_convert(lead_id: int, deal_category_id: int = 0) -> str:
    """
    Usa esta tool para CONVERTIR un Lead en Deal + Contacto cuando el cliente muestra interés real de compra.
    
    Args:
        lead_id: ID del Lead.
        deal_category_id: ID del pipeline de ventas (0=Default, o específico).
    """
    if not lead_id:
        return "Error: lead_id es requerido."

    try:
        # 1. Obtener datos del Lead
        lead_data = call_bitrix_method("crm.lead.get", {"id": lead_id})
        lead = lead_data.get("result")
        if not lead:
            return f"Error: no se encontró el Lead {lead_id}."

        result_msg = f"Lead {lead_id} procesado."
        contact_id = None
        deal_id = None

        # 2. Crear Contacto
        contact_fields = {
            "NAME": lead.get("NAME", ""),
            "LAST_NAME": lead.get("LAST_NAME", ""),
            "OPENED": "Y",
            "SOURCE_ID": lead.get("SOURCE_ID", ""),
        }
        if lead.get("PHONE"):
            contact_fields["PHONE"] = lead["PHONE"]
        if lead.get("EMAIL"):
            contact_fields["EMAIL"] = lead["EMAIL"]
        if lead.get("ASSIGNED_BY_ID"):
            contact_fields["ASSIGNED_BY_ID"] = lead["ASSIGNED_BY_ID"]

        contact_result = call_bitrix_method("crm.contact.add", {"fields": contact_fields})
        contact_id = contact_result.get("result")
        if contact_id:
            result_msg += f" Contacto: {contact_id}."
        else:
            result_msg += f" Error creando Contacto."

        # 3. Crear Deal
        deal_title = lead.get("TITLE", f"Deal desde Lead {lead_id}")
        deal_fields = {
            "TITLE": deal_title,
            "OPENED": "Y",
            "SOURCE_ID": lead.get("SOURCE_ID", ""),
            "CATEGORY_ID": deal_category_id
        }
        if contact_id:
            deal_fields["CONTACT_ID"] = contact_id
        if lead.get("ASSIGNED_BY_ID"):
            deal_fields["ASSIGNED_BY_ID"] = lead["ASSIGNED_BY_ID"]
        if lead.get("OPPORTUNITY"):
            deal_fields["OPPORTUNITY"] = lead["OPPORTUNITY"]
        if lead.get("CURRENCY_ID"):
            deal_fields["CURRENCY_ID"] = lead["CURRENCY_ID"]

        deal_result = call_bitrix_method("crm.deal.add", {"fields": deal_fields})
        deal_id = deal_result.get("result")
        if deal_id:
            result_msg += f" Deal: {deal_id}."
        else:
            result_msg += f" Error creando Deal."

        # 4. Marcar Lead como convertido
        if contact_id or deal_id:
            call_bitrix_method("crm.lead.update", {
                "id": lead_id,
                "fields": {"STATUS_ID": "CONVERTED"}
            })

        return result_msg

    except Exception as e:
        return f"Error convirtiendo lead: {e}"
