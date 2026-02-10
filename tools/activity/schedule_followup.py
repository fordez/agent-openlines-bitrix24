"""
Herramienta para programar seguimiento automático.
"""
from tools.activity.create_activity import create_activity
from datetime import datetime, timedelta

def schedule_followup(contact_id: str, text: str, delay_days: int = 1) -> str:
    """
    Programa una llamada o tarea de seguimiento para el futuro.
    
    Args:
        contact_id: ID del contacto.
        text: Descripción del seguimiento (ej: "Llamar para confirmar interés").
        delay_days: Días de espera para el seguimiento. Default 1.
        
    Returns:
        str: Resultado de la creación.
    """
    if not contact_id:
        return "Falta contact_id"

    deadline = (datetime.now() + timedelta(days=delay_days)).strftime("%Y-%m-%d 10:00:00")
    
    # Creamos una actividad tipo LLAMADA (2) por defecto para seguimiento
    return create_activity(
        owner_type_id=3, # Contacto
        owner_id=contact_id, 
        description=text, 
        deadline=deadline, 
        type_id=2, # Call (Llamada)
        subject=f"Seguimiento: {text[:30]}..."
    )
