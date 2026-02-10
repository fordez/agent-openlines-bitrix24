"""
Herramienta para reactivar leads inactivos.
"""
from app.auth import call_bitrix_method

def reactivate_lead(lead_id: str) -> str:
    """
    Reabre o reactiva un Lead (Prospecto) que estaba cerrado o perdido.
    
    Args:
        lead_id: ID del Lead (Prospecto).
        
    Returns:
        str: Resultado de la reactivación.
    """
    if not lead_id:
        return "Falta lead_id"

    # Status "NEW" es típicamente el inicial.
    # STATUS_ID es el campo para Leads. (STAGE_ID es para Deals)
    
    fields = {
        "STATUS_ID": "NEW", 
        "OPENED": "Y" # Marcar como abierto
    }

    try:
        call_bitrix_method("crm.lead.update", {
            "id": lead_id,
            "fields": fields
        })
        return f"Lead {lead_id} reactivado a estado NUEVO."
    except Exception as e:
        return f"Error reactivando lead: {e}"
