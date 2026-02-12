"""
Tool to list CRM activities for a specific entity.
"""
from app.auth import call_bitrix_method

async def crm_activity_list(entity_id: int, entity_type: str) -> str:
    """
    Lista las actividades vinculadas a un Lead o Deal.
    
    Args:
        entity_id: ID del Lead o Deal.
        entity_type: "LEAD" o "DEAL".
    """
    etype_id = 1 if entity_type.upper() == "LEAD" else 2
    
    try:
        result = await call_bitrix_method("crm.activity.list", {
            "filter": {
                "OWNER_ID": entity_id,
                "OWNER_TYPE_ID": etype_id
            },
            "select": ["ID", "SUBJECT", "START_TIME", "END_TIME", "COMPLETED", "TYPE_ID"]
        })
        
        activities = result.get("result", [])
        if not activities:
            return f"No se encontraron actividades para la entidad {entity_id}."
            
        output = f"Actividades para {entity_type} {entity_id}:\n"
        for a in activities:
            status = "✅ Completada" if a.get("COMPLETED") == "Y" else "⏳ Pendiente"
            output += f"- ID: {a.get('ID')} | {a.get('SUBJECT')} | {status} | Inicio: {a.get('START_TIME')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando actividades: {e}"
