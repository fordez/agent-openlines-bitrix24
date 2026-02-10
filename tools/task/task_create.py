"""
Tool to create tasks for human follow-up.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

def task_create(title: str, description: str, responsible_id: int = None, deadline_hours: int = 24) -> str:
    """
    Crear tareas para que humanos continúen acciones necesarias.
    Endpoint: tasks.task.add
    
    Args:
        title: Título de la tarea.
        description: Descripción detallada de lo que debe hacer el humano.
        responsible_id: ID del usuario responsable. Si no se envía si asignará al creador (bot).
        deadline_hours: Plazo en horas para la tarea. Por defecto 24h.
        
    Returns:
        str: ID de la tarea creada o error.
    """
    if not title:
        return "Error: Falta título de la tarea."

    # Calculate deadline
    deadline = (datetime.now() + timedelta(hours=deadline_hours)).strftime('%Y-%m-%dT%H:%M:%S')

    fields = {
        "TITLE": title,
        "DESCRIPTION": description,
        "DEADLINE": deadline,
        "PRIORITY": 1, # 1 = Average
    }
    
    if responsible_id:
        fields["RESPONSIBLE_ID"] = responsible_id

    try:
        result = call_bitrix_method("tasks.task.add", {"fields": fields})
        task = result.get("result", {}).get("task", {})
        return f"Tarea creada: {task.get('id')} - {task.get('title')}"
        
    except Exception as e:
        return f"Error creando tarea: {e}"
