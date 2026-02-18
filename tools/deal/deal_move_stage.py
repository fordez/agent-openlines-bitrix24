"""
Tool to change the deal pipeline stage.
"""
from app.auth import call_bitrix_method

async def deal_move_stage(deal_id: str, stage_id: str) -> str:
    """
    Cambiar la etapa del pipeline del deal (ej. negociación, propuesta, seguimiento).
    Endpoint: crm.deal.update
    
    Args:
        deal_id: ID del deal.
        stage_id: ID de la etapa destino (ej: "NEW", "PREPARATION", "PREPAYMENT").
                  PROHIBIDO usar etapas de cierre ("WON", "LOSE").
                  
    Returns:
        str: Mensaje de éxito o error.
    """
    if not deal_id or not stage_id:
        return "Error: Faltan argumentos (deal_id, stage_id)"

    # Safeguard: Do not allow moving to closing stages
    closing_stages = ["WON", "LOSE", "CLOSED"]
    if stage_id.upper() in closing_stages:
        return f"Error: No está permitido cerrar negocios desde esta herramienta (etapa {stage_id} bloqueada)."

    try:
        await call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": {
                "STAGE_ID": stage_id
            }
        })
        return f"Deal {deal_id} movido a la etapa {stage_id}."
        
    except Exception as e:
        return f"Error moviendo etapa del deal {deal_id}: {e}"
