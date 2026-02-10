"""
Tool to add activity notes to CRM (using timeline comments for simplicity).
"""
from app.auth import call_bitrix_method

def activity_add(activity_type: str, subject: str, description: str, owner_id: str = None, owner_type_id: int = 1) -> str:
    """
    Registrar notas o seguimiento de la interacción en el CRM.
    Usa crm.timeline.comment.add para Leads/Deals/Contacts por ser más directo.
    
    Args:
        activity_type: Tipo (solo referencial en la nota).
        subject: Asunto (se incluirá en el texto).
        description: Descripción.
        owner_id: ID del Lead/Deal/Contacto.
        owner_type_id: 1=Lead, 2=Deal, 3=Contact.
        
    Returns:
        str: ID del comentario creado.
    """
    if not description:
        return "Error: Faltan argumentos (description)"
    if not owner_id:
        return "Error: Falta owner_id"

    # Map owner_type_id to string
    entity_type = "lead"
    if owner_type_id == 2:
        entity_type = "deal"
    elif owner_type_id == 3:
        entity_type = "contact"
    elif owner_type_id == 4:
        entity_type = "company"
        
    full_comment = f"🤖 **Actividad AI ({activity_type})**\nSubject: {subject}\n\n{description}"

    try:
        # Use simpler timeline comment
        result = call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": owner_id,
                "ENTITY_TYPE": entity_type,
                "COMMENT": full_comment
            }
        })
        return f"Actividad registrada (Nota): {result.get('result')}"
        
    except Exception as e:
        return f"Error registrando actividad: {e}"
