"""
Tool to get full information of a deal by ID.
"""
from app.auth import call_bitrix_method

def deal_get(deal_id: str) -> str:
    """
    Obtener información completa de un deal por ID.
    Endpoint: crm.deal.get
    
    Args:
        deal_id: ID del deal.
        
    Returns:
        str: JSON string con la información del deal o mensaje de error.
    """
    if not deal_id:
        return "Error: Falta deal_id"

    try:
        result = call_bitrix_method("crm.deal.get", {"id": deal_id})
        deal = result.get("result")
        
        if not deal:
            return f"No se encontró el deal con ID {deal_id}"
            
        # Formatear una respuesta legible para el agente
        output = (
            f"Deal ID: {deal.get('ID')}\n"
            f"Título: {deal.get('TITLE')}\n"
            f"Etapa: {deal.get('STAGE_ID')}\n"
            f"Monto: {deal.get('OPPORTUNITY')} {deal.get('CURRENCY_ID')}\n"
            f"Contacto ID: {deal.get('CONTACT_ID')}\n"
            f"Responsable ID: {deal.get('ASSIGNED_BY_ID')}\n"
            f"Cerrado: {deal.get('CLOSED')}\n"
            f"Fecha Creación: {deal.get('DATE_CREATE')}\n"
        )
        return output
        
    except Exception as e:
        return f"Error obteniendo deal {deal_id}: {e}"
