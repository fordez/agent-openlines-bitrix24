"""
Tool to get available calendar types.
"""
from app.auth import call_bitrix_method

def calendar_get_types() -> str:
    """
    Consultar tipos de calendario disponibles (personal, grupo, recurso).
    Endpoint: calendar.type.get
    
    Returns:
        str: Lista de tipos de calendario o error.
    """
    try:
        result = call_bitrix_method("calendar.type.get", {})
        types = result.get("result", [])
        
        if not types:
            return "No se encontraron tipos de calendario."
            
        output = "Tipos de Calendario disponibles:\n"
        for t in types:
            output += f"- {t.get('XML_ID')}: {t.get('NAME')} (Description: {t.get('DESCRIPTION')})\n"
            
        return output
        
    except Exception as e:
        return f"Error obteniendo tipos de calendario: {e}"
