"""
Tool to list calendar events to avoid conflicts in Bitrix24.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta
import sys

async def calendar_event_list(from_date: str = None, to_date: str = None) -> str:
    """
    Usa esta tool para LEER LA AGENDA y saber qué reuniones hay programadas en un rango.
    Si no das fechas, toma los próximos 7 díasales.
    
    Args:
        from_date: Fecha inicio (YYYY-MM-DD). Usa siempre el año y fecha actual del contexto.
        to_date: Fecha fin (YYYY-MM-DD). Usa siempre el año y fecha actual del contexto.
    """
    sys.stderr.write(f"  📅 Tool calendar_event_list: from={from_date}, to={to_date}\n")
    sys.stderr.write("  🔑 Creds: (usando TokenManager centralizado)\n")

    # Default dates
    if not from_date:
        from_date = datetime.now().strftime('%Y-%m-%d')
    if not to_date:
        to_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    from app.auth import get_current_user_id
    owner_id = await get_current_user_id()
    
    params = {
        "type": "user",
        "ownerId": owner_id,
        "from": from_date,
        "to": to_date
    }
    
    try:
        result = await call_bitrix_method("calendar.event.get", params)
        events = result.get("result", [])
        
        if not events:
            return f"No hay eventos programados entre {from_date} y {to_date}."
            
        output = f"Agenda ({from_date} a {to_date}):\n"
        for e in events:
            output += (
                f"- [{e.get('ID')}] {e.get('NAME')}: "
                f"{e.get('DATE_FROM')} - {e.get('DATE_TO')} "
                f"(Lugar: {e.get('LOCATION', 'No especificado')})\n"
            )
        return output

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en calendar_event_list: {e}\n")
        return f"Error consultando agenda: {e}"
