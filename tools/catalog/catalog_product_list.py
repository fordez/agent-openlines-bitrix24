"""
Tool to list products in a category.
"""
from app.auth import call_bitrix_method

async def catalog_product_list(section_id: int) -> str:
    """
    Usa esta tool para LISTAR PRODUCTOS dentro de una categoría/sección.
    
    Args:
        section_id: ID de la sección/categoría.
    """
    if not section_id:
        return "Error: Falta section_id"

    try:
        result = await call_bitrix_method("crm.product.list", {
            "order": {"NAME": "ASC"},
            "filter": {"SECTION_ID": section_id},
            "select": ["ID", "NAME", "PRICE", "CURRENCY_ID"]
        })
        products = result.get("result", [])
        
        if not products:
            return f"No se encontraron productos en la categoría {section_id}."
            
        output = f"Productos en Categoría {section_id}:\n"
        for p in products:
            output += f"- ID: {p.get('ID')} | {p.get('NAME')} | Precio: {p.get('PRICE')} {p.get('CURRENCY_ID')}\n"
            
        return output
        
    except Exception as e:
        return f"Error listando productos: {e}"
