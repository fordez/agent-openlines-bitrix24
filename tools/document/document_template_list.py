"""
Tool to list document templates.
"""
from app.auth import call_bitrix_method

def document_template_list(entity_type_id: int = 2) -> str:
    """
    Usa esta tool para ver qué PLANTILLAS de documentos (cotizaciones, facturas) existen.
    
    Args:
        entity_type_id: 1=Lead, 2=Deal (Default). Usa según el contexto (si tratas con Lead o Deal).
    """
    params = {}
    if entity_type_id:
        params["filter"] = {"entityTypeId": entity_type_id}

    try:
        result = call_bitrix_method("crm.documentgenerator.template.list", params)
        # Debug
        # print(f"DEBUG: document_template_list result: {result}")
        
        # result['result'] is a dict like {'templates': [...]}, not a list directly
        data = result.get("result", {})
        if isinstance(data, list):
             templates = data # Some bitrix methods return list directly
        else:
             templates = data.get("templates", [])
        
        if not templates:
            return "No se encontraron plantillas de documentos."
            
        output = "Plantillas Disponibles:\n"
        for t in templates:
            if isinstance(t, dict):
                output += f"- ID: {t.get('id')} | Nombre: {t.get('name')} (Module: {t.get('moduleId')})\n"
            else:
                # Fallback if list of IDs or strings
                output += f"- {t}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando plantillas: {e}"
