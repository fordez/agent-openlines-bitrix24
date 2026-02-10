"""
Herramienta para reagendar eventos en el calendario.
"""
from app.auth import call_bitrix_method

def reschedule_event(event_id: str, from_date: str, to_date: str) -> str:
    """
    Cambia la fecha y hora de una reunión o evento existente.
    
    Args:
        event_id: ID del evento a reagendar.
        from_date: Nueva fecha de inicio (YYYY-MM-DD HH:MM:SS) o (YYYY-MM-DD).
        to_date: Nueva fecha de fin (YYYY-MM-DD HH:MM:SS) o (YYYY-MM-DD).
        
    Returns:
        str: Resultado de la operación.
    """
    if not event_id or not from_date or not to_date:
        return "Faltan datos obligatorios (event_id, from_date, to_date)"

    fields = {
        "id": event_id,
        "from": from_date,
        "to": to_date
    }
    
    # Si las fechas no tienen hora, marcar skip_time
    if len(from_date) == 10:
         fields["skip_time"] = "Y"
    else:
         fields["skip_time"] = "N"

    try:
        call_bitrix_method("calendar.event.update", fields)
        return f"Evento {event_id} reagendado para: {from_date} - {to_date}."
    except Exception as e:
        return f"Error reagendando evento: {e}"
