"""
Tool to fetch CRM field definitions (schema).
"""
from app.auth import call_bitrix_method

async def crm_fields_get(entity_type: str) -> str:
    """
    Obtener el esquema de campos (nombres, tipos, etiquetas) de una entidad CRM.
    
    Args:
        entity_type: "LEAD", "DEAL", "CONTACT", "COMPANY".
    """
    method_map = {
        "LEAD": "crm.lead.fields",
        "DEAL": "crm.deal.fields",
        "CONTACT": "crm.contact.fields",
        "COMPANY": "crm.company.fields"
    }
    
    etype = entity_type.upper()
    method = method_map.get(etype)
    
    if not method:
        return f"Error: Entidad '{entity_type}' no soportada."

    try:
        result = await call_bitrix_method(method, {})
        fields = result.get("result", {})
        
        output = f"Esquema de campos para {etype}:\n"
        for code, info in fields.items():
            title = info.get("title") or info.get("formLabel") or code
            ftype = info.get("type")
            is_req = " (Requerido)" if info.get("isRequired") else ""
            output += f"- {code}: {title} [{ftype}]{is_req}\n"
            
        return output
        
    except Exception as e:
        return f"Error obteniendo esquemas: {e}"
