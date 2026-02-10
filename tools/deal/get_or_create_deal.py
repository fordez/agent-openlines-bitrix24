"""
Herramienta para obtener o crear un deal (negocio) para un contacto.
"""
from app.auth import call_bitrix_method

def get_or_create_deal(contact_id: str, title: str = None) -> str:
    """
    Busca un deal activo asociado al contacto. Si no existe, crea uno nuevo.
    
    Args:
        contact_id: ID del contacto.
        title: Título del nuevo deal (si se crea uno). Por defecto "Negocio con [Contact ID]".
        
    Returns:
        str: El ID del deal.
    """
    if not contact_id:
        return "Falta contact_id"

    # 1. Buscar deals activos asociados al contacto
    # Filtramos por CONTACT_ID y stages que NO sean ganados/perdidos (simplificado)
    # En Bitrix, CLOSED='N' indica abierto.
    try:
        result = call_bitrix_method("crm.deal.list", {
            "filter": {
                "CONTACT_ID": contact_id,
                "CLOSED": "N"  # Solo deals abiertos
            },
            "select": ["ID", "TITLE", "STAGE_ID"],
            "order": {"DATE_CREATE": "DESC"},
            "limit": 1
        })
        
        deals = result.get("result", [])
        if deals:
            deal = deals[0]
            print(f"✅ Deal activo encontrado: {deal['ID']} - {deal['TITLE']}")
            return str(deal['ID'])
            
    except Exception as e:
        print(f"Error buscando deals: {e}")

    # 2. Si no hay, crear nuevo deal
    print(f"⚠️ No hay deal activo para contacto {contact_id}. Creando uno nuevo...")
    
    new_title = title or f"Negocio con Contacto {contact_id}"
    
    fields = {
        "TITLE": new_title,
        "CONTACT_ID": contact_id,
        "OPENED": "Y",
        # "STAGE_ID": "NEW" # Por defecto
    }
    
    try:
        result = call_bitrix_method("crm.deal.add", {"fields": fields})
        new_deal_id = result.get("result")
        print(f"✅ Nuevo deal creado: {new_deal_id}")
        return str(new_deal_id)
    except Exception as e:
        print(f"❌ Error creando deal: {e}")
        return "Error creating deal"
