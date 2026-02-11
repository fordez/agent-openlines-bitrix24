"""
Tool to add products to a deal.
"""
from app.auth import call_bitrix_method

async def deal_add_products(deal_id: int, products: list[dict]) -> str:
    """
    Usa esta tool para AGREGAR productos seleccionados al Deal (Cotización).
    
    Args:
        deal_id: ID del Deal.
        products: Lista de productos (dict con 'PRODUCT_ID', 'PRICE', 'QUANTITY').
                  Ej: [{'PRODUCT_ID': 10, 'PRICE': 100, 'QUANTITY': 1}]
    """
    if not deal_id or not products:
        return "Error: Faltan argumentos (deal_id, products)"

    output = ""
    error_count = 0

    for p in products:
        # Normalizar para ser resiliente a lo que envíe el LLM
        pid = p.get("PRODUCT_ID") or p.get("product_id")
        price = p.get("PRICE") or p.get("price")
        qty = p.get("QUANTITY") or p.get("quantity", 1)
        curr = p.get("CURRENCY_ID") or p.get("currency")

        fields = {
            "OWNER_TYPE": "D", # D = Deal
            "OWNER_ID": deal_id,
            "PRODUCT_ID": pid,
            "PRICE": price,
            "QUANTITY": qty
        }
        
        if curr:
            fields["CURRENCY_ID"] = curr

        try:
            # crm.productrow.add (legacy but standard for deals) or crm.item.productrow.add (new item based)
            # Para Deals estándar, crm.productrow.add es lo usual.
            result = await call_bitrix_method("crm.productrow.add", {"fields": fields})
            output += f"- Producto {p.get('product_id')} agregado (Row ID: {result.get('result')})\n"
        except Exception as e:
            output += f"- Error agregando producto {p.get('product_id')}: {e}\n"
            error_count += 1
            
    if error_count == len(products):
        return f"Falló agregar todos los productos:\n{output}"
        
    return f"Proceso finalizado:\n{output}"
