"""
Herramienta para actualizar un Lead en Bitrix24.
Usa el método: crm.lead.update
"""
from app.auth import call_bitrix_method
import json


def lead_update(lead_id: int, fields: dict) -> str:
    """
    Usa esta tool para ACTUALIZAR datos de un Lead existente (ej: agregar teléfono, corregir nombre).
    
    Args:
        lead_id: ID del Lead.
        fields: Diccionario con campos a actualizar (ej: {"NAME": "Juan", "PHONE": [{"VALUE": "555..."}]}).
    """
    if not lead_id:
        return "Error: lead_id es requerido."

    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except Exception:
            return "Error: fields debe ser un dict o JSON válido."

    if not fields:
        return "Error: se requiere al menos un campo para actualizar."

    # Normalizar campos de teléfono y email al formato Bitrix24
    bitrix_fields = {}
    for k, v in fields.items():
        k_upper = k.upper()
        if k_upper == "PHONE":
            bitrix_fields["PHONE"] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
        elif k_upper == "EMAIL":
            bitrix_fields["EMAIL"] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
        else:
            bitrix_fields[k_upper] = v

    try:
        result = call_bitrix_method("crm.lead.update", {
            "id": lead_id,
            "fields": bitrix_fields
        })
        if result.get("result"):
            return f"Lead {lead_id} actualizado exitosamente."
        else:
            error = result.get("error_description", result)
            return f"Error actualizando lead: {error}"
    except Exception as e:
        return f"Error actualizando lead: {e}"
