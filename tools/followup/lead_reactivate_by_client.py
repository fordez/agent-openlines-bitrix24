"""
Tool to reactivate lead when client interacts.
"""
from app.auth import call_bitrix_method

def lead_reactivate_by_client(lead_id: int) -> str:
    """
    Usa esta tool cuando un cliente retoma el contacto en un Lead que estaba cerrado o inactivo.
    Reactiva el Lead automáticamente a estado 'NEW'.

    Args:
        lead_id: ID del Lead a reactivar.
    """
    if not lead_id:
        return "Error: Falta lead_id"

    try:
        # Check current status first? Or just force update.
        # Let's force update to 'NEW' or equivalent open status. 
        # Usually "NEW" or "IN_PROCESS". Let's assume "NEW" for now.
        status_id = "NEW"
        
        result = call_bitrix_method("crm.lead.update", {
            "id": lead_id,
            "fields": {"STATUS_ID": status_id}
        })
        
        if result.get("result"):
             return f"Lead {lead_id} reactivado exitosamente a estado {status_id}."
        else:
             return f"No se pudo reactivar el Lead {lead_id}."
             
    except Exception as e:
        return f"Error reactivando lead: {e}"
