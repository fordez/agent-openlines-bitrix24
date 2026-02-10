"""
Tool to mark the deal as closed (WON or LOST).
"""
from app.auth import call_bitrix_method

def deal_mark_closed(deal_id: str, status: str, comment: str = None) -> str:
    """
    Marcar el deal como cerrado: GANADO o PERDIDO según contexto.
    Endpoint: crm.deal.update (STAGE_ID = WON / LOST)
    
    Args:
        deal_id: ID del deal.
        status: "WON" (Ganado) o "LOST" (Perdido).
        comment: Comentario opcional sobre el motivo del cierre.
        
    Returns:
        str: Mensaje de éxito o error.
    """
    if not deal_id or not status:
        return "Error: Faltan argumentos (deal_id, status)"
        
    status_upper = status.upper()
    if status_upper not in ["WON", "LOST"]:
        return "Error: status debe ser 'WON' o 'LOST'."
        
    # Mapeo a STAGE_ID de Bitrix (normalmente "WON" y "LOSE")
    # Nota: En Bitrix Cloud standard suele ser "WON" y "LOSE". 
    # Si el usuario menciona "LOST" lo mapeamos a "LOSE".
    bitrix_stage_id = "WON" if status_upper == "WON" else "LOSE"

    try:
        fields = {
            "STAGE_ID": bitrix_stage_id
        }
        
        # Si hay comentario, lo agregamos (opcional, dependiendo si COMMENTS existe)
        # O mejor, llamamos al endpoint de timeline si se requiere historial, 
        # pero aquí podemos intentar actualizar el campo COMMENTS si existe.
        if comment:
            fields["COMMENTS"] = f"Cierre ({status}): {comment}"
            
        call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": fields
        })
        
        # Si hay comentario, también lo agregamos al timeline para que quede registro claro
        if comment:
             try:
                call_bitrix_method("crm.timeline.comment.add", {
                    "fields": {
                        "ENTITY_ID": deal_id,
                        "ENTITY_TYPE": "deal",
                        "COMMENT": f"🏁 Deal Cerrado como {status}. Motivo: {comment}"
                    }
                })
             except:
                 pass # No fallar si el comentario falla, lo importante es el estado
        
        return f"Deal {deal_id} marcado como {status} ({bitrix_stage_id})."
        
    except Exception as e:
        return f"Error cerrando deal {deal_id}: {e}"
