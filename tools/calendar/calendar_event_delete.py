"""
Tool to delete/cancel calendar events.
"""
from app.auth import call_bitrix_method

async def calendar_event_delete(event_id: int) -> str:
    """
    Usa esta tool para CANCELAR/BORRAR una reunión.
    
    Args:
        event_id: ID del evento a eliminar.
    """
    if not event_id:
        return "Error: Falta event_id"

    try:
        result = await call_bitrix_method("calendar.event.delete", {"id": event_id})
        res = result.get("result")
        if res:
             return f"Evento {event_id} eliminado exitosamente."
        else:
             return f"No se pudo eliminar el evento {event_id} (quizás no existe o no tienes permisos)."
    except Exception as e:
        return f"Error eliminando evento: {e}"
