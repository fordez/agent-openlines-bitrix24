"""
Herramienta para crear actividades en el CRM (llamadas, reuniones, tareas).
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def create_activity(
    owner_type_id: int, 
    owner_id: str, 
    description: str, 
    deadline: str = None, 
    type_id: int = 3,
    subject: str = "Seguimiento Automático"
) -> str:
    """
    Crea una actividad en el CRM.
    
    Args:
        owner_type_id: Tipo de entidad dueña (1=Lead, 2=Deal, 3=Contact, 4=Company).
        owner_id: ID de la entidad dueña.
        description: Descripción detallada de la actividad.
        deadline: Fecha límite (YYYY-MM-DD HH:MM:SS). Si no se da, se pone +1 día.
        type_id: Tipo de actividad (1=Meeting, 2=Call, 3=Task, 4=Email). Default 3 (Task).
        subject: Asunto de la actividad.
        
    Returns:
        str: ID de la actividad creada.
    """
    if not owner_id:
        return "Falta owner_id"

    if not deadline:
        # Por defecto mañana
        deadline = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    fields = {
        "OWNER_TYPE_ID": owner_type_id,
        "OWNER_ID": owner_id,
        "TYPE_ID": type_id,
        "SUBJECT": subject,
        "START_TIME": deadline, # Bitrix usa start/end time para calendario, deadline para tareas
        "END_TIME": deadline,
        "DESCRIPTION": description,
        "COMPLETED": "N",
        "PRIORITY": 2, # Normal
        "RESPONSIBLE_ID": 1 # Asignar al admin/usuario por defecto
    }

    try:
        result = call_bitrix_method("crm.activity.add", {"fields": fields})
        activity_id = result.get("result")
        if activity_id:
            return f"Actividad creada ID: {activity_id}"
        else:
            return f"Error creando actividad: {result}"
    except Exception as e:
        return f"Error creando actividad: {e}"
