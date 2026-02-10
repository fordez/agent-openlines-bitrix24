"""
Tool to list categories in a catalog.
"""
from app.auth import call_bitrix_method

def catalog_category_list(catalog_id: int) -> str:
    """
    Usa esta tool para ver las CATEGORÍAS (Secciones) dentro de un catálogo específico.
    
    Args:
        catalog_id: ID del catálogo a explorar.
    """
    if not catalog_id:
        return "Error: Falta catalog_id"

    try:
        # Usamos crm.productsection.list que es más común para CRM
        result = call_bitrix_method("crm.productsection.list", {
            "order": {"NAME": "ASC"},
            "filter": {"CATALOG_ID": catalog_id}
        })
        sections = result.get("result", [])
        
        if not sections:
            return f"No se encontraron categorías en el catálogo {catalog_id}."
            
        output = f"Categorías del Catálogo {catalog_id}:\n"
        for s in sections:
            output += f"- ID: {s.get('ID')} | Nombre: {s.get('NAME')} | ParentID: {s.get('SECTION_ID')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando categorías: {e}"
