"""
Tool to update/reschedule calendar events.
"""
from app.auth import call_bitrix_method, get_current_user_id
import sys

async def calendar_event_update(event_id: int, title: str = None, start_time: str = None, end_time: str = None, description: str = None, remind_mins: int = None) -> str:
    """
    Modifica una reunión existente. Permite repromgramar o cambiar detalles.
    """
    if not event_id:
        return "Error: event_id es requerido."

    sys.stderr.write(f"  📅 Tool calendar_event_update: ID {event_id}\n")

    try:
        owner_id = await get_current_user_id()
        
        fields = {
            "id": event_id,
            "ownerId": owner_id,
            "type": "user"
        }
        
        if title: fields["name"] = title
        if start_time: fields["from"] = start_time
        if end_time: fields["to"] = end_time
        if description: fields["description"] = description
        if remind_mins is not None:
            fields["remind"] = [{"type": "min", "count": remind_mins}]
        
        result = await call_bitrix_method("calendar.event.update", fields)
        
        if result.get("result"):
            return f"Evento {event_id} actualizado exitosamente."
        else:
            error = result.get("error_description", result)
            return f"Error al actualizar evento: {error}"

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en calendar_event_update: {e}\n")
        return f"Error técnico: {e}"
