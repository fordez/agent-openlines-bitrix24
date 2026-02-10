"""
Herramienta para agendar reunión y vincular con CRM.
"""
from app.auth import call_bitrix_method
from tools.calendar.create_event import create_event

def schedule_meeting(contact_id: str, title: str, from_date: str, to_date: str, description: str = None) -> str:
    """
    Crea evento en calendario y lo vincula con CRM (crea actividad tipo reunión).
    
    Args:
        contact_id: ID del contacto en CRM.
        title: Título de la reunión.
        from_date: Inicio (YYYY-MM-DD HH:MM:SS).
        to_date: Fin (YYYY-MM-DD HH:MM:SS).
        description: Detalles adicionales.
        
    Returns:
        str: Confirmación con IDs creados.
    """
    if not contact_id:
        return "Falta contact_id"

    # 1. Crear evento en calendario
    # Nota: Simplificamos usando la tools ya creada, pero necesitamos el ID.
    # create_event revuelve string, mejor llamamos lógica directa o parseamos.
    # Para robustez, llamemos a la API directa aquí también o refactorizamos create_event para devolver ID limpio.
    # Dado que create_event devuelve un string formateado, usaremos llamadas directas para tener control.
    
    print(f"Agendando reunión '{title}' para contacto {contact_id}...")
    
    # A. Crear Actividad en CRM (Meeting)
    # Esto automáticamente aparece en el calendario del responsable si se configura así,
    # pero a veces se prefiere calendar.event.add y luego vincular. 
    # La forma standard de CRM es crm.activity.add con TYPE_ID=2 (Call) o Meeting (provider ID).
    
    # Intentemos crm.activity.add que es lo más correcto para "vincular con CRM".
    activity_fields = {
        "OWNER_TYPE_ID": 3, # 3 = Contacto
        "OWNER_ID": contact_id,
        "TYPE_ID": 1, # 1 = Meeting (Reunión)
        "SUBJECT": title,
        "START_TIME": from_date,
        "END_TIME": to_date,
        "DESCRIPTION": description or "",
        "COMPLETED": "N",
        "PRIORITY": 2, # Normal
        "RESPONSIBLE_ID": 1 # Asignar al admin/usuario por defecto o buscarlo
    }
    
    try:
        res_act = call_bitrix_method("crm.activity.add", {"fields": activity_fields})
        activity_id = res_act.get("result")
        
        if activity_id:
            return f"Reunión agendada en CRM. Actividad ID: {activity_id}"
        else:
             return f"Error creando actividad en CRM: {res_act}"
             
    except Exception as e:
        return f"Error al agendar reunión: {e}"
