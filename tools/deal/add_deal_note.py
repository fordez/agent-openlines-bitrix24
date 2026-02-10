"""
Herramienta para agregar notas a un deal.
"""
from app.auth import call_bitrix_method

def add_deal_note(deal_id: str, note: str) -> str:
    """
    Guarda notas importantes de la conversación en el deal.
    Usa el timeline de Bitrix24.
    
    Args:
        deal_id: ID del deal.
        note: Contenido de la nota.
        
    Returns:
        str: Resultado de la operación.
    """
    if not deal_id or not note:
        return "Faltan argumentos"

    try:
        call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": f"📝 **Nota de Agente AI:**\n{note}"
            }
        })
        return f"Nota agregada al deal {deal_id}."
    except Exception as e:
        return f"Error agregando nota: {e}"
