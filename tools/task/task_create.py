"""
Tool to create tasks for human follow-up in Bitrix24, with CRM linking support.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta
import sys

async def task_create(title: str, description: str, responsible_id: int = None, deadline_hours: int = 24, entity_id: int = None, entity_type: str = "LEAD") -> str:
    """
    Crear tareas para seguimiento humano. Puede vincularse a un Lead o Deal.
    
    Args:
        title: Título de la tarea.
        description: Detalles de la acción requerida.
        responsible_id: ID del usuario responsable.
        deadline_hours: Plazo en horas (default 24).
        entity_id: ID de la entidad CRM a vincular (opcional).
        entity_type: "LEAD", "DEAL", "CONTACT", "COMPANY".
    """
    sys.stderr.write(f"  🔍 Tool task_create: {title}\n")
    
    if not title:
        return "Error: Falta título de la tarea."

    deadline = (datetime.now() + timedelta(hours=deadline_hours)).strftime('%Y-%m-%dT%H:%M:%S')

    if not responsible_id:
        from app.auth import get_current_user_id
        responsible_id = await get_current_user_id()

    # Prepara campos básicos
    fields = {
        "TITLE": title,
        "DESCRIPTION": description,
        "DEADLINE": deadline,
        "PRIORITY": 2, # Alta
        "RESPONSIBLE_ID": responsible_id
    }

    # Vincular a CRM (Bitrix usa el prefijo en UF_CRM_TASK)
    if entity_id:
        prefix = "L" # Lead por defecto
        if entity_type.upper() == "DEAL": prefix = "D"
        elif entity_type.upper() == "CONTACT": prefix = "C"
        elif entity_type.upper() == "COMPANY": prefix = "CO"
        
        # Bitrix espera una lista de strings para vínculos CRM en tareas
        fields["UF_CRM_TASK"] = [f"{prefix}_{entity_id}"]

    try:
        result = await call_bitrix_method("tasks.task.add", {"fields": fields})
        task_id = result.get("result", {}).get("task", {}).get("id")
        
        if task_id:
            msg = f"Tarea '{title}' creada (ID: {task_id})."
            if entity_id:
                msg += f" Vinculada a {entity_type} {entity_id}."
            return msg
        else:
            error = result.get("error_description", result)
            return f"Error de Bitrix: {error}"
            
    except Exception as e:
        return f"Error técnico creando tarea: {e}"
