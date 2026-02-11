"""
Tool to get full calendar event details.
"""
from app.auth import call_bitrix_method

async def calendar_event_get(event_id: int) -> str:
    """
    Obtener toda la información de un evento de calendario por su ID.
    
    Args:
        event_id: ID del evento.
    """
    if not event_id:
        return "Error: Falta event_id"

    try:
        result = await call_bitrix_method("calendar.event.getbyid", {"id": event_id})
        event = result.get("result")
        
        if not event:
            return f"No se encontró el evento {event_id}."
            
        output = f"Detalles del Evento {event_id}:\n"
        output += f"- Título: {event.get('NAME')}\n"
        output += f"- Inicio: {event.get('DATE_FROM')}\n"
        output += f"- Fin: {event.get('DATE_TO')}\n"
        output += f"- Descripción: {event.get('DESCRIPTION') or 'Sin descripción'}\n"
        output += f"- Ubicación: {event.get('LOCATION') or 'Sin ubicación'}\n"
        
        return output
        
    except Exception as e:
        return f"Error obteniendo evento: {e}"
