"""
Tool to get full contact details.
"""
from app.auth import call_bitrix_method

async def contact_get(contact_id: int) -> str:
    """
    Obtener toda la información de un Contacto por su ID.
    
    Args:
        contact_id: ID del Contacto.
    """
    if not contact_id:
        return "Error: Falta contact_id"

    try:
        result = await call_bitrix_method("crm.contact.get", {"id": contact_id})
        contact = result.get("result")
        
        if not contact:
            return f"No se encontró el Contacto {contact_id}."
            
        output = f"Detalles del Contacto {contact_id}:\n"
        for k, v in contact.items():
            if v and not isinstance(v, (list, dict)):
                output += f"- {k}: {v}\n"
            elif v:
                output += f"- {k}: {str(v)}\n"
                
        return output
        
    except Exception as e:
        return f"Error obteniendo contacto: {e}"
