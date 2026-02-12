"""
Tool to list tasks in Bitrix24, with optional filtering by CRM entity.
"""
from app.auth import call_bitrix_method

async def task_list(entity_id: int = None, entity_type: str = "LEAD") -> str:
    """
    Lista tareas en Bitrix24.
    
    Args:
        entity_id: ID del Lead, Deal, etc. para filtrar.
        entity_type: "LEAD", "DEAL", "CONTACT", "COMPANY".
    """
    filter_params = {}
    if entity_id:
        prefix = "L"
        if entity_type.upper() == "DEAL": prefix = "D"
        elif entity_type.upper() == "CONTACT": prefix = "C"
        elif entity_type.upper() == "COMPANY": prefix = "CO"
        filter_params["UF_CRM_TASK"] = f"{prefix}_{entity_id}"

    try:
        # tasks.task.list uses a specific response structure
        result = await call_bitrix_method("tasks.task.list", {
            "filter": filter_params,
            "select": ["ID", "TITLE", "STATUS", "DEADLINE", "RESPONSIBLE_ID"]
        })
        
        tasks_data = result.get("result", {}).get("tasks", [])
        if not tasks_data:
            return "No se encontraron tareas."
            
        output = "Tareas encontradas:\n"
        for t in tasks_data:
            status_map = {"2": "Pendiente", "3": "En Proceso", "5": "Completada"}
            status = status_map.get(t.get("status"), t.get("status"))
            output += f"- ID: {t.get('id')} | {t.get('title')} | Estado: {status} | Límite: {t.get('deadline')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando tareas: {e}"
