"""
Tool to add client objection to deal.
"""
from app.auth import call_bitrix_method

async def deal_add_client_objection(deal_id: int, objection: str) -> str:
    """
    Usa esta tool cuando el cliente exprese una queja, duda o motivo para no comprar (ej: "Es muy caro").
    Registra la objeción en el Deal para análisis futuro.

    Args:
        deal_id: ID del Deal.
        objection: Texto exacto o resumen breve de la objeción del cliente.
    """
    if not deal_id or not objection:
        return "Error: Faltan argumentos"

    try:
        # First get existing comments to append? Or just overwrite?
        # Bitrix 'COMMENTS' field overwrites. 
        # Ideally use crm.timeline.comment.add for history.
        # But requirement said "crm.deal.update (campo COMMENTS o personalizado)".
        # I will append to existing COMMENTS if possible, or use timeline comment which is safer and better practice.
        # Let's stick to adding a timeline comment as it is "adding an objection" effectively tracking it.
        # But if strict on "crm.deal.update", let's try to fetch and append.
        
        # Method 1: Append to COMMENTS (Risk: concurrency)
        # get_res = await call_bitrix_method("crm.deal.get", {"id": deal_id})
        # old_comments = get_res.get("result", {}).get("COMMENTS", "")
        # new_comments = old_comments + "\n[Objeción Cliente]: " + objection
        # ... update ...
        
        # Method 2: Timeline comment (Safe, History) -> "crm.timeline.comment.add"
        # Since I am "updating existing agent", and instructed to use "crm.deal.update (campo COMMENTS)", I should probably follow instruction or improve.
        # "crm.deal.update (campo COMMENTS ...)" implies modifying the field.
        # I will use "crm.deal.update" appending the text.
        
        get_res = await call_bitrix_method("crm.deal.get", {"id": deal_id})
        old_comments = get_res.get("result", {}).get("COMMENTS") or ""
        
        # HTML line break for bitrix comments field is usually <br> or \n
        new_comments = old_comments + f"\n[OBJECIÓN]: {objection}"
        
        result = await call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": {"COMMENTS": new_comments}
        })
        
        if result.get("result"):
             return f"Objeción registrada en Deal {deal_id}."
        else:
             return "No se pudo registrar la objeción."

    except Exception as e:
        return f"Error registrando objeción: {e}"
