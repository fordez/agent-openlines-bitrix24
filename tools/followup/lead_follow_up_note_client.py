"""
Tool to add internal note to lead.
"""
from app.auth import call_bitrix_method

def lead_follow_up_note_client(lead_id: int, note: str) -> str:
    """
    Usa esta tool para guardar información CLAVE que mencione el cliente (presupuesto, fechas, preferencias).
    Agrega una nota interna visible para el equipo.

    Args:
        lead_id: ID del Lead.
        note: Información relevante a guardar.
    """
    if not lead_id or not note:
        return "Error: Faltan argumentos"

    try:
        # Using timeline.comment.add is cleaner for notes than appending to single COMMENTS field.
        # But instructions said "crm.lead.comment.add o crm.lead.update (campo COMMENTS)".
        # crm.timeline.comment.add is the modern equivalent of "adding a comment".
        
        result = call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": lead_id,
                "ENTITY_TYPE": "lead",
                "COMMENT": note
            }
        })
        
        if result.get("result"):
             return f"Nota agregada al Lead {lead_id}."
        else:
             # Fallback to appending COMMENTS if timeline fails (e.g. permission)
             get_res = call_bitrix_method("crm.lead.get", {"id": lead_id})
             old_comments = get_res.get("result", {}).get("COMMENTS") or ""
             new_comments = old_comments + f"\n[NOTA BOT]: {note}"
             
             upd_res = call_bitrix_method("crm.lead.update", {
                 "id": lead_id,
                 "fields": {"COMMENTS": new_comments}
             })
             if upd_res.get("result"):
                 return f"Nota agregada al Lead {lead_id} (campo COMMENTS)."
             else:
                 return "No se pudo agregar la nota."
             
    except Exception as e:
        return f"Error agregando nota: {e}"
