"""
Tool to set reminders for calendar events.
"""
from app.auth import call_bitrix_method

async def calendar_event_set_reminder(event_id: str, minutes: int = 60, owner_id: int = 1) -> str:
    """
    Configurar recordatorios automáticos para los asistentes del evento.
    Endpoint: calendar.event.update (campo REMIND)
    
    Args:
        event_id: ID del evento.
        minutes: Minutos antes del evento para recordar.
        owner_id: ID del dueño del calendario. Default 1.
        
    Returns:
        str: Resultado de la configuración.
    """
    if not event_id:
        return "Error: Falta event_id"

    # Format for REMIND field depending on Bitrix API version.
    # Usually: [{"type": "min", "count": 60}]
    
    remind = [{"type": "min", "count": minutes}]

    try:
        result = await call_bitrix_method("calendar.event.update", {
            "id": event_id,
            "type": "user",
            "ownerId": owner_id,
            "remind": remind
        })
        return f"Recordatorio configurado para {minutes} minutos antes en evento {event_id}."
    except Exception as e:
        return f"Error configurando recordatorio: {e}"
