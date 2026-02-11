"""
Tool to get full lead details.
"""
from app.auth import call_bitrix_method

async def lead_get(lead_id: int) -> str:
    """
    Obtener toda la información de un Lead por su ID.
    
    Args:
        lead_id: ID del Lead.
    """
    if not lead_id:
        return "Error: Falta lead_id"

    try:
        result = await call_bitrix_method("crm.lead.get", {"id": lead_id})
        lead = result.get("result")
        
        if not lead:
            return f"No se encontró el Lead {lead_id}."
            
        output = f"Detalles del Lead {lead_id}:\n"
        for k, v in lead.items():
            if v and not isinstance(v, (list, dict)):
                output += f"- {k}: {v}\n"
            elif v:
                output += f"- {k}: {str(v)}\n"
                
        return output
        
    except Exception as e:
        return f"Error obteniendo lead: {e}"
