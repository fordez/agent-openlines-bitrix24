"""
Tool to schedule next action for lead by agent.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def lead_next_action_client(lead_id: int, description: str, deadline_mins: int = 60) -> str:
    """
    Usa esta tool para SUGERIR qué debe hacer el agente humano a continuación con este Lead.
    Ejemplos: "Llamar cliente", "Enviar brochure". Se registra como nota en el timeline.

    Args:
        lead_id: ID del Lead.
        description: Acción concreta sugerida basada en la charla actual.
        deadline_mins: En cuantos minutos debería hacerse (default 60).
    """
    if not lead_id or not description:
        return "Error: Faltan argumentos"

    try:
        # Fallback to timeline comment
        full_comment = f"📅 **ACCIÓN SUGERIDA (Lead)**\nDescripción: {description}\nDeadline sugerido: {deadline_mins} min"
        
        result = call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": lead_id,
                "ENTITY_TYPE": "lead",
                "COMMENT": full_comment
            }
        })
        
        if result.get("result"):
             return f"Próxima acción registrada en timeline del Lead {lead_id}."
        else:
             return "No se pudo registrar la acción."
             
    except Exception as e:
        return f"Error registrando acción: {e}"
