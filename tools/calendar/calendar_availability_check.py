"""
Tool to check availability of participants.
"""
from app.auth import call_bitrix_method
from datetime import datetime

async def calendar_availability_check(start_time: str, end_time: str) -> str:
    """
    Usa esta tool para VERIFICAR DISPONIBILIDAD antes de agendar.
    Retorna si el horario está libre u ocupado.
    
    Args:
        start_time: Fecha y hora de inicio (YYYY-MM-DD HH:MM:SS).
        end_time: Fecha y hora de fin (YYYY-MM-DD HH:MM:SS).
        
    Returns:
        str: Reporte de disponibilidad (huecos ocupados).
    """
    if not from_date or not to_date or not users:
        return "Error: Faltan argumentos (from_date, to_date, users list)"

    try:
        result = await call_bitrix_method("calendar.accessibility.get", {
            "from": from_date,
            "to": to_date,
            "users": users
        })
        
        accessibility = result.get("result", {})
        
        if not accessibility:
            return "Todos los usuarios parecen disponibles (no hay datos de ocupación)."
            
        output = f"Ocupación ({from_date} a {to_date}):\n"
        for user_id, events in accessibility.items():
            output += f"Usuario {user_id}:\n"
            for e in events:
                output += f"  - Ocupado: {e.get('DATE_FROM')} hasta {e.get('DATE_TO')} ({e.get('NAME', 'Evento')})\n"
                
        return output

    except Exception as e:
        return f"Error verificando disponibilidad: {e}"
