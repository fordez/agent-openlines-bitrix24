"""
Herramienta para consultar disponibilidad en el calendario.
"""
from app.auth import call_bitrix_method
from datetime import datetime

def get_availability(from_date: str, to_date: str, users: list = None) -> str:
    """
    Consulta horarios disponibles en el calendario.
    
    Args:
        from_date: Fecha inicio en formato YYYY-MM-DD.
        to_date: Fecha fin en formato YYYY-MM-DD.
        users: Lista de IDs de usuarios a consultar (opcional).
        
    Returns:
        str: Información de disponibilidad o eventos existentes.
    """
    if not from_date or not to_date:
        return "Faltan fechas (from_date, to_date)"

    # Formato Bitrix suele requerir YYYY-MM-DD
    try:
        # Validar formato fechas simplemente
        datetime.strptime(from_date, "%Y-%m-%d")
        datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return "Formato de fecha inválido. Usa YYYY-MM-DD."

    params = {
        "from": from_date,
        "to": to_date
    }
    
    if users:
        params["users"] = users

    try:
        # calendar.accessibility.get devuelve la ocupación
        result = call_bitrix_method("calendar.accessibility.get", params)
        data = result.get("result", {})
        
        # Formatear respuesta para el LLM
        if not data:
            return "No se encontró información de disponibilidad (posiblemente todo libre)."
            
        output = "Ocupación encontrada:\n"
        for user_id, events in data.items():
            output += f"Usuario {user_id}:\n"
            for event in events:
                output += f"  - {event.get('DATE_FROM')} a {event.get('DATE_TO')} ({event.get('NAME', 'Ocupado')})\n"
                
        return output

    except Exception as e:
        return f"Error consultando disponibilidad: {e}"
