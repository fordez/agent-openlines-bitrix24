"""
Tool to create new calendar events.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def calendar_event_create(title: str, start_time: str, end_time: str, description: str = "") -> str:
    """
    Usa esta tool para AGENDAR una cita/reunión en el calendario del agente.
    Útil cuando el cliente confirma disponibilidad.
    
    Args:
        str: ID del evento creado.
    """
    if not name or not from_ts:
        return "Error: Faltan argumentos (name, from_ts)"

    # Calculate to_ts if missing
    if not to_ts:
        try:
            # Try parsing with time
            dt_from = datetime.strptime(from_ts, '%Y-%m-%d %H:%M:%S')
            dt_to = dt_from + timedelta(minutes=duration_mins)
            to_ts = dt_to.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            # Maybe just date provided?
            try:
                dt_from = datetime.strptime(from_ts, '%Y-%m-%d')
                dt_to = dt_from  # All day usually, or default logic
                # For simplicity, if date only, assume +1 day for all day, but user usually wants appointments.
                # Let's assume standard format required.
                return "Error: Formato de fecha debe ser 'YYYY-MM-DD HH:MM:SS'"
            except:
                return "Error parsing date format."

    fields = {
        "type": "user",
        "name": name,
        "from": from_ts,
        "to": to_ts,
        "description": description,
        "location": location,
        "ownerId": owner_id,
        "section": 0 # Default calendar
    }
    
    if attendees:
        fields["attendees"] = attendees

    try:
        result = call_bitrix_method("calendar.event.add", fields)
        return f"Evento creado exitosamente. ID: {result.get('result')}"
        
    except Exception as e:
        return f"Error creando evento: {e}"
