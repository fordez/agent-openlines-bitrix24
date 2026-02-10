"""
Herramienta para actualizar actividades en el CRM.
"""
from app.auth import call_bitrix_method

def update_activity(activity_id: str, fields: dict) -> str:
    """
    Actualiza datos de una actividad.
    
    Args:
        activity_id: ID de la actividad.
        fields: Diccionario con campos a actualizar (SUBJECT, DESCRIPTION, etc).
        
    Returns:
        str: Resultado de la operación.
    """
    if not activity_id:
        return "Falta activity_id"

    # Preparar params para crm.activity.update
    params = {
        "id": activity_id,
        "fields": fields
    }

    try:
        result = call_bitrix_method("crm.activity.update", params)
        if result.get("result"):
             return f"Actividad {activity_id} actualizada."
        else:
             return f"Error actualizando actividad: {result}"
    except Exception as e:
        return f"Error actualizando actividad: {e}"
