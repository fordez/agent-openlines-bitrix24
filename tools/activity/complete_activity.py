"""
Herramienta para completar actividades en el CRM.
"""
from app.auth import call_bitrix_method

def complete_activity(activity_id: str) -> str:
    """
    Marca una actividad como completada.
    
    Args:
        activity_id: ID de la actividad.
        
    Returns:
        str: Resultado de la operación.
    """
    if not activity_id:
        return "Falta activity_id"

    params = {
        "id": activity_id,
        "fields": {
            "COMPLETED": "Y"
        }
    }

    try:
        result = call_bitrix_method("crm.activity.update", params)
        if result.get("result"):
             return f"Actividad {activity_id} completada."
        else:
             return f"Error completando actividad: {result}"
    except Exception as e:
        return f"Error completando actividad: {e}"
