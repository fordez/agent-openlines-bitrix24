"""
Tool to list available product catalogs.
"""
from app.auth import call_bitrix_method

async def catalog_list() -> str:
    """
    Usa esta tool para ver QUÉ catálogos de productos hay disponibles (ej: "Paquetes", "Vuelos").
    
    Returns:
        str: Lista de catálogos con sus IDs.
    """
    try:
        result = await call_bitrix_method("crm.catalog.list", {})
        catalogs = result.get("result", [])
        
        if not catalogs:
            return "No se encontraron catálogos."
            
        output = "Catálogos Disponibles:\n"
        for c in catalogs:
            output += f"- ID: {c.get('ID')} | Nombre: {c.get('NAME')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando catálogos: {e}"
