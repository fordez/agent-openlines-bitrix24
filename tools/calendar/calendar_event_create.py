"""
Tool to create new calendar events in Bitrix24.
"""
from app.auth import call_bitrix_method
import sys

async def calendar_event_create(title: str, start_time: str, end_time: str, description: str = "", remind_mins: int = 60) -> str:
    """
    Agrega un evento al calendario.
    Si se proporciona remind_mins, se configura un recordatorio automático.
    """
    if not title or not start_time or not end_time:
        return "Error: title, start_time y end_time son requeridos."

    sys.stderr.write(f"  📅 Tool calendar_event_create: {title} ({start_time})\n")

    try:
        from app.auth import get_current_user_id
        owner_id = await get_current_user_id()
        
        fields = {
            "type": "user",
            "ownerId": owner_id,
            "name": title,
            "from": start_time,
            "to": end_time,
            "description": description,
            "section": 0
        }

        if remind_mins:
            fields["remind"] = [{"type": "min", "count": remind_mins}]
    
        result = await call_bitrix_method("calendar.event.add", fields)
        event_id = result.get("result")
        
        if event_id:
            return f"Evento '{title}' agendado exitosamente. ID: {event_id}. Recordatorio: {remind_mins} min."
        else:
            error = result.get("error_description", result)
            return f"Error de Bitrix al crear evento: {error}"
        
    except Exception as e:
        sys.stderr.write(f"  ❌ Error en calendar_event_create: {e}\n")
        return f"Error técnico: {e}"
