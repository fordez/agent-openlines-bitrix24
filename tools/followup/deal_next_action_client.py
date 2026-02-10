"""
Tool to schedule next action for deal by agent.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def deal_next_action_client(deal_id: int, description: str, deadline_mins: int = 60) -> str:
    """
    Usa esta tool para SUGERIR la siguiente acción operativa sobre el Deal.
    Ejemplos: "Preparar contrato", "Cotizar vuelo". Se registra en el timeline.

    Args:
        deal_id: ID del Deal.
        description: Acción sugerida al humano.
        deadline_mins: Tiempo sugerido para completarla.
    """
    if not deal_id or not description:
        return "Error: Faltan argumentos"

    try:
        # Fallback to timeline comment due to activity API restrictions on this instance
        full_comment = f"📅 **ACCIÓN SUGERIDA (Deal)**\nDescripción: {description}\nDeadline sugerido: {deadline_mins} min"
        
        result = call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": full_comment
            }
        })
        
        if result.get("result"):
             return f"Próxima acción registrada en timeline del Deal {deal_id}."
        else:
             return "No se pudo registrar la acción."
             
    except Exception as e:
        return f"Error registrando acción: {e}"
