"""
Herramienta para actualizar eventos en el calendario.
"""
from app.auth import call_bitrix_method

def update_event(event_id: str, fields: dict) -> str:
    """
    Modifica fecha, hora o datos del evento.
    
    Args:
        event_id: ID del evento a modificar.
        fields: Diccionario con campos a actualizar (name, from, to, description, etc).
        
    Returns:
        str: Resultado de la operación.
    """
    if not event_id:
        return "Falta event_id"

    params = {
        "id": event_id
    }
    # Mezclar fields en params
    params.update(fields)

    try:
        call_bitrix_method("calendar.event.update", params)
        return f"Evento {event_id} actualizado correctamente."
    except Exception as e:
        return f"Error actualizando evento: {e}"
