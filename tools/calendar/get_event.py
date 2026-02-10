"""
Herramienta para obtener detalles de un evento.
"""
from app.auth import call_bitrix_method
import json

def get_event(event_id: str) -> str:
    """
    Consulta información de un evento existente.
    
    Args:
        event_id: ID del evento.
        
    Returns:
        str: Detalles del evento en formato texto/json.
    """
    if not event_id:
        return "Falta event_id"

    try:
        result = call_bitrix_method("calendar.event.getbyid", {"id": event_id})
        data = result.get("result")
        
        if not data:
            return "Evento no encontrado."
            
        return json.dumps(data, indent=2, ensure_ascii=False)

    except Exception as e:
        return f"Error obteniendo evento: {e}"
