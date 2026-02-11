"""
Tool to search products by name.
"""
from app.auth import call_bitrix_method

async def catalog_product_search(name: str) -> str:
    """
    Usa esta tool para BUSCAR productos por nombre (ej: "Madrid", "Hotel playa").
    
    Args:
        name: Término de búsqueda.
    """
    if not name:
        return "Error: Falta query (término de búsqueda)"

    try:
        # Filtro SEARCH_CONTENT suele funcionar, o %NAME%
        result = await call_bitrix_method("crm.product.list", {
            "order": {"NAME": "ASC"},
            "filter": {"%NAME": name}, # Búsqueda parcial por nombre
            "select": ["ID", "NAME", "PRICE", "CURRENCY_ID", "SECTION_ID"]
        })
        products = result.get("result", [])
        
        if not products:
            return f"No se encontraron productos coincidiendo con '{name}'."
            
        output = f"Resultados búsqueda '{name}':\n"
        for p in products:
            output += f"- ID: {p.get('ID')} | {p.get('NAME')} | Precio: {p.get('PRICE')} {p.get('CURRENCY_ID')} (Cat: {p.get('SECTION_ID')})\n"
            
        return output
        
    except Exception as e:
        return f"Error buscando productos: {e}"
