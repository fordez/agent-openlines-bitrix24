"""
Tool to update general deal information.
"""
from app.auth import call_bitrix_method
import json

def deal_update_info(deal_id: str, fields: dict) -> str:
    """
    Actualizar datos generales del deal: título, monto, responsable, campos personalizados.
    Endpoint: crm.deal.update
    
    Args:
        deal_id: ID del deal.
        fields: Diccionario con campos a actualizar.
                Ej: {"TITLE": "Nuevo Título", "OPPORTUNITY": 1000, "ASSIGNED_BY_ID": 5}
                
    Returns:
        str: Mensaje de éxito o error.
    """
    if not deal_id:
        return "Error: Falta deal_id"

    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except:
            return "Error: fields must be a dict or valid json string"

    try:
        # Validar que no se intente cambiar STAGE_ID aquí si se prefiere usar deal_move_stage,
        # pero Bitrix lo permite. La instrucción dice "Actualizar datos generales".
        # Dejaremos que pase cualquier campo por flexibilidad.
        
        call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": fields
        })
        return f"Deal {deal_id} actualizado correctamente."
        
    except Exception as e:
        return f"Error actualizando deal {deal_id}: {e}"
