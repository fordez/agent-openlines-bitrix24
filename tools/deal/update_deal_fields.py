"""
Herramienta para actualizar campos de un deal.
"""
from app.auth import call_bitrix_method
import json

def update_deal_fields(deal_id: str, fields: dict) -> str:
    """
    Actualiza datos comerciales del deal (producto, presupuesto, etc.).
    
    Args:
        deal_id: ID del deal.
        fields: Diccionario con campos a actualizar.
                Ej: {"OPPORTUNITY": 5000, "CURRENCY_ID": "USD", "COMMENTS": "..."}
        
    Returns:
        str: Resultado de la operación.
    """
    if not deal_id:
        return "Falta deal_id"

    # Preparar campos
    bitrix_fields = {}
    
    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except:
             return "Error: fields must be a dict or valid json string"

    for k, v in fields.items():
        k_upper = k.upper()
        # Mapeo simple de algunos campos comunes
        if k_upper in ["TITLE", "OPPORTUNITY", "CURRENCY_ID", "COMMENTS", "ADDITIONAL_INFO"]:
            bitrix_fields[k_upper] = v
        elif k_upper == "PRESUPUESTO":
            bitrix_fields["OPPORTUNITY"] = v
        else:
            bitrix_fields[k_upper] = v

    try:
        call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": bitrix_fields
        })
        return f"Deal {deal_id} actualizado exitosamente."
    except Exception as e:
        return f"Error actualizando deal: {e}"
