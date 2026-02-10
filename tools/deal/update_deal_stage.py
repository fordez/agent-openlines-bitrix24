"""
Herramienta para actualizar la etapa de un deal.
"""
from app.auth import call_bitrix_method

def update_deal_stage(deal_id: str, stage_id: str) -> str:
    """
    Mueve el deal a otra etapa del pipeline.
    
    Args:
        deal_id: ID del deal.
        stage_id: ID de la etapa (ej: "NEW", "PREPARATION", "WON", "LOSE").
                  Consultar configuración de Bitrix para IDs exactos.
        
    Returns:
        str: Resultado de la operación.
    """
    if not deal_id or not stage_id:
        return "Faltan argumentos (deal_id, stage_id)"

    try:
        call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": {
                "STAGE_ID": stage_id
            }
        })
        return f"Deal {deal_id} movido a etapa {stage_id}."
    except Exception as e:
        return f"Error actualizando etapa del deal: {e}"
