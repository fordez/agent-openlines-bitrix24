"""
Herramienta para crear eventos en el calendario.
"""
from app.auth import call_bitrix_method

def create_event(title: str, from_date: str, to_date: str, description: str = None, attendees: list = None) -> str:
    """
    Agenda reunión, llamada o demo en el calendario.
    
    Args:
        title: Título del evento.
        from_date: Inicio (YYYY-MM-DD HH:MM:SS) o (YYYY-MM-DD).
        to_date: Fin (YYYY-MM-DD HH:MM:SS) o (YYYY-MM-DD).
        description: Descripción del evento.
        attendees: Lista de IDs de usuarios invitados (opcional).
        
    Returns:
        str: ID del evento creado o error.
    """
    if not title or not from_date or not to_date:
        return "Faltan datos obligatorios (title, from_date, to_date)"

    fields = {
        "name": title,
        "from": from_date,
        "to": to_date,
        "description": description or "",
        "section": "0", # Calendario principal
        "skip_time": "N" # N = toma en cuenta la hora
    }
    
    # Si las fechas no tienen hora, podemos asumir evento de día completo o dejar que bitrix decida
    if len(from_date) == 10: # YYYY-MM-DD
        fields["skip_time"] = "Y"

    if attendees:
        # attendees se pasa diferente según la versión de API, a veces es 'attendees' list
        fields["attendees"] = attendees

    try:
        result = call_bitrix_method("calendar.event.add", params=fields) # calendar.event.add usa params directos, no "fields" wrapper a veces. Verifiquemos auth wrapper.
        # call_bitrix_method wrap params in json body. calendar.event.add expects args directly in body.
        
        if "result" in result:
             event_id = result["result"]
             return f"Evento creado exitosamente: {event_id}"
        else:
             return f"Error creando evento: {result}"

    except Exception as e:
        return f"Error al crear evento: {e}"
