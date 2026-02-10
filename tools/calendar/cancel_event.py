"""
Herramienta para cancelar eventos en el calendario.
"""
from app.auth import call_bitrix_method

def cancel_event(event_id: str) -> str:
    """
    Cancela una reunión (elimina el evento).
    
    Args:
        event_id: ID del evento a cancelar.
        
    Returns:
        str: Resultado de la operación.
    """
    if not event_id:
        return "Falta event_id"

    try:
        call_bitrix_method("calendar.event.delete", {"id": event_id})
        return f"Evento {event_id} cancelado/eliminado."
    except Exception as e:
        return f"Error cancelando evento: {e}"
