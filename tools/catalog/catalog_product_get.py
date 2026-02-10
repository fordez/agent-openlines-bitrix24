"""
Tool to get full product details.
"""
from app.auth import call_bitrix_method

async def catalog_product_get(product_id: int) -> str:
    """
    Obtener detalles completos de un producto o servicio por su ID.
    Endpoint: crm.product.get
    
    Args:
        product_id: ID del producto.
        
    Returns:
        str: Detalles del producto.
    """
    if not product_id:
        return "Error: Falta product_id"

    try:
        result = await call_bitrix_method("crm.product.get", {"id": product_id})
        product = result.get("result")
        
        if not product:
            return f"No se encontró el producto {product_id}."
            
        output = f"Detalles Producto {product_id}:\n"
        output += f"Nombre: {product.get('NAME')}\n"
        output += f"Precio: {product.get('PRICE')} {product.get('CURRENCY_ID')}\n"
        output += f"Descripción: {product.get('DESCRIPTION', 'Sin descripción')}\n"
        output += f"Sección (Cat): {product.get('SECTION_ID')}\n"
        output += f"Activo: {product.get('ACTIVE')}\n"
        
        return output
        
    except Exception as e:
        return f"Error obteniendo producto: {e}"
