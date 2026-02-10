"""
Tool to list calendar events to avoid conflicts.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def calendar_event_list(from_date: str = None, to_date: str = None) -> str:
    """
    Usa esta tool para LEER LA AGENDA y saber qué reuniones hay programadas en un rango.
    Si no das fechas, toma los próximos 7 días.
    
    Args:
        from_date: Fecha inicio (YYYY-MM-DD).
        to_date: Fecha fin (YYYY-MM-DD).
    """
    # Default dates
    if not from_date:
        from_date = datetime.now().strftime('%Y-%m-%d')
    if not to_date:
        to_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    params = {
        "type": "user",
        "from": from_date,
        "to": to_date
    }
    
    # We remove owner_id support to simplify, assuming current user (bot/agent)

    try:
        # Changed to calendar.event.get as .list might be invalid/deprecated
        result = call_bitrix_method("calendar.event.get", params)
        events = result.get("result", [])
        
        if not events:
            return f"No hay eventos programados entre {from_date} y {to_date}."
            
        output = f"Agenda ({from_date} a {to_date}):\n"
        for e in events:
            output += (
                f"- [{e.get('ID')}] {e.get('NAME')}: "
                f"{e.get('DATE_FROM')} - {e.get('DATE_TO')} "
                f"(Location: {e.get('LOCATION')})\n"
            )
        return output

    except Exception as e:
        return f"Error consultando agenda: {e}"
