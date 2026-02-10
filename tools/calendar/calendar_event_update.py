"""
Tool to update/reschedule calendar events.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

async def calendar_event_update(event_id: int, title: str = None, description: str = None) -> str:
    """
    Usa esta tool para MODIFICAR una reunión existente (ej: cambiar título o notas).
    
    Args:
        event_id: ID del evento.
        str: Resultado de la actualización.
    """
    if not event_id:
        return "Error: Falta event_id"

    fields = {
        "id": event_id,
        "ownerId": owner_id,
        "type": "user"
    }
    
    if name: fields["name"] = name
    if description: fields["description"] = description
    
    # Handle rescheduling
    if from_ts:
        fields["from"] = from_ts
        if to_ts:
            fields["to"] = to_ts
        elif duration_mins:
            try:
                dt_from = datetime.strptime(from_ts, '%Y-%m-%d %H:%M:%S')
                dt_to = dt_from + timedelta(minutes=duration_mins)
                fields["to"] = dt_to.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass # If format fails, maybe user provided just date?
    
    try:
        result = await call_bitrix_method("calendar.event.update", fields)
        return f"Evento {event_id} actualizado exitosamente: {result.get('result')}"
    except Exception as e:
        return f"Error actualizando evento: {e}"
