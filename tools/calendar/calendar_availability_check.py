"""
Tool to check availability of participants in Bitrix24 calendar.
"""
from app.auth import call_bitrix_method
import sys

async def calendar_availability_check(start_time: str, end_time: str) -> str:
    """
    Usa esta tool para VERIFICAR DISPONIBILIDAD antes de agendar.
    Retorna si el horario está ocupado.
    
    Args:
        start_time: Fecha y hora de inicio (YYYY-MM-DD HH:MM:SS).
        end_time: Fecha y hora de fin (YYYY-MM-DD HH:MM:SS).
    
    IMPORTANT INSTRUCTION FOR AGENT:
    1. DO NOT list available times. NEVER.
    2. CHECK availability and RECOMMEND ONLY the single closest available slot (One date, One time).
    3. REPLY with that single recommendation: "I have availability on [Date] at [Time]. Should I book it?"
    4. Be extremely brief.
    """
    sys.stderr.write(f"  📅 Tool calendar_availability_check: start='{start_time}', end='{end_time}'\n")
    sys.stderr.write("  🔑 Creds: (usando TokenManager centralizado)\n")

    if not start_time or not end_time:
        return "Error: Faltan argumentos (start_time, end_time)"

    try:
        # Por defecto verificamos la disponibilidad del bot (actual usuario)
        # Obtenemos el ID del bot via user.current si es necesario, 
        # pero Bitrix suele asumir el usuario actual si no se envían IDs.
        
        from app.auth import get_current_user_id
        bot_id = await get_current_user_id()
        
        result = await call_bitrix_method("calendar.accessibility.get", {
            "from": start_time,
            "to": end_time,
            "users": [bot_id]
        })
        
        accessibility = result.get("result", {})
        
        if not accessibility:
            return "El horario está disponible (no se encontraron bloqueos)."
            
        output = f"Reporte de ocupación entre {start_time} y {end_time}:\n"
        for user_id, events in accessibility.items():
            if events:
                output += f"Usuario {user_id} está OCUPADO en:\n"
                for e in events:
                    output += f"  - {e.get('NAME', 'Evento')}: {e.get('DATE_FROM')} a {e.get('DATE_TO')}\n"
            else:
                output += f"Usuario {user_id} está LIBRE.\n"
                
        return output

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en calendar_availability_check: {e}\n")
        return f"Error verificando disponibilidad: {e}"
