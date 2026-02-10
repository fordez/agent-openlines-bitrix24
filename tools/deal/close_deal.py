"""
Herramienta para cerrar un deal.
"""
from app.auth import call_bitrix_method

def close_deal(deal_id: str, won: bool = True, close_comment: str = None) -> str:
    """
    Cierra el deal como ganado o perdido.
    
    Args:
        deal_id: ID del deal.
        won: True si se ganó, False si se perdió.
        close_comment: Comentario final opcional.
        
    Returns:
        str: Resultado de la operación.
    """
    if not deal_id:
        return "Falta deal_id"

    # Etapas estándar de cierre (pueden variar según config de Bitrix)
    # WON = "WON"
    # LOSE = "LOSE"
    
    stage_id = "WON" if won else "LOSE"
    
    fields = {
        "STAGE_ID": stage_id
    }
    
    if close_comment:
        fields["COMMENTS"] = f"Cierre ({stage_id}): {close_comment}"

    try:
        call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": fields
        })
        
        status_text = "GANADO" if won else "PERDIDO"
        return f"Deal {deal_id} cerrado como {status_text}."
        
    except Exception as e:
        return f"Error cerrando deal: {e}"
