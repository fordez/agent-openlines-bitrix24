"""
Tool to add notes or comments to the deal timeline.
"""
from app.auth import call_bitrix_method

def deal_add_note(deal_id: str, note: str) -> str:
    """
    Agregar notas o comentarios al timeline del deal para registrar conversaciones o acciones.
    Endpoint: crm.timeline.comment.add
    
    Args:
        deal_id: ID del deal.
        note: Contenido de la nota.
        
    Returns:
        str: Mensaje de éxito o error.
    """
    if not deal_id or not note:
        return "Error: Faltan argumentos (deal_id, note)"

    try:
        call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": f"📝 Nota de Agente:\n{note}"
            }
        })
        return f"Nota agregada al deal {deal_id}."
        
    except Exception as e:
        return f"Error agregando nota al deal {deal_id}: {e}"
