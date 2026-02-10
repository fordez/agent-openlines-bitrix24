"""
Tool to detect deal stage for client updates.
"""
from app.auth import call_bitrix_method

def deal_detect_stage_for_client(deal_id: int) -> str:
    """
    Usa esta tool cuando el cliente pregunte "¿Cómo va mi proceso?" o necesites saber en qué etapa está el negocio.
    Retorna la etapa actual del Deal para informar al cliente.

    Args:
        deal_id: ID del Deal.
    """
    if not deal_id:
        return "Error: Falta deal_id"

    try:
        result = call_bitrix_method("crm.deal.get", {"id": deal_id})
        deal = result.get("result", {})
        
        if not deal:
            return f"No se encontró el Deal {deal_id}."
            
        stage_id = deal.get("STAGE_ID")
        # To get stage Name we would need crm.status.list but usually ID is descriptive enough 
        # or we return ID and let Agent interpret.
        # But allow user to know "En Proceso" vs "C1:NEW".
        # We'll return just the ID/Name stored in deal.
        
        return f"El Deal {deal_id} se encuentra en la etapa: {stage_id}"
        
    except Exception as e:
        return f"Error detectando etapa: {e}"
