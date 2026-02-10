"""
Tool to update product rows in a deal.
"""
from app.auth import call_bitrix_method

async def deal_update_products(row_id: int, fields: dict) -> str:
    """
    Modificar un producto/fila específica en un Deal existente (cantidad, precio, etc).
    Endpoint: crm.productrow.update
    
    Args:
        row_id: ID de la fila (Product Row ID, NO Product ID). Se obtiene al listar rows o agregar.
        fields: Campos a actualizar. Ej: {"quantity": 2, "price": 90}
        
    Returns:
        str: Resultado de la actualización.
    """
    if not row_id or not fields:
        return "Error: Faltan argumentos (row_id, fields)"

    try:
        # crm.productrow.update
        result = await call_bitrix_method("crm.productrow.update", {
            "id": row_id,
            "fields": fields
        })
        
        if result.get("result"):
             return f"Fila de producto {row_id} actualizada exitosamente."
        else:
             return f"No se pudo actualizar la fila {row_id}."

    except Exception as e:
        return f"Error actualizando producto en deal: {e}"
