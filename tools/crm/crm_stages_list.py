"""
Tool to fetch CRM stages/statuses.
"""
from app.auth import call_bitrix_method

async def crm_stages_list(entity_type: str = "DEAL") -> str:
    """
    Listar los estados o etapas disponibles en el CRM para un proceso.
    
    Args:
        entity_type: "LEAD" (Status) o "DEAL" (Stages).
    """
    # En Bitrix, los estados se manejan vía crm.status.list
    # Filter by ENTITY_ID: STATUS (Leads), DEAL_STAGE (Deals)
    
    entity_id = "STATUS"
    if entity_type.upper() == "DEAL":
        entity_id = "DEAL_STAGE"

    try:
        result = await call_bitrix_method("crm.status.list", {
            "filter": {"ENTITY_ID": entity_id},
            "order": {"SORT": "ASC"}
        })
        statuses = result.get("result", [])
        
        if not statuses:
            return f"No se encontraron estados para {entity_type}."
            
        output = f"Estados/Etapas para {entity_type.upper()}:\n"
        for s in statuses:
            output += f"- ID: {s.get('STATUS_ID')} | Nombre: {s.get('NAME')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando estados: {e}"
