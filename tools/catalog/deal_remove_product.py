"""
Tool to remove product row from a deal.
"""
from app.auth import call_bitrix_method

async def deal_remove_product(row_id: int) -> str:
    """
    Eliminar un producto/fila de un Deal existente.
    Endpoint: crm.productrow.delete
    
    Args:
        row_id: ID de la fila (Product Row ID) a eliminar.
        
    Returns:
        str: Resultado de la eliminación.
    """
    if not row_id:
        return "Error: Falta row_id"

    try:
        result = await call_bitrix_method("crm.productrow.delete", {"id": row_id})
        
        if result.get("result"):
             return f"Fila de producto {row_id} eliminada exitosamente."
        else:
             return f"No se pudo eliminar la fila {row_id}."
             
    except Exception as e:
        return f"Error eliminando producto de deal: {e}"
