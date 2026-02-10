"""
Herramienta para resolver identidad en Bitrix24.
"""
from app.auth import call_bitrix_method

def resolve_identity(phone: str = None, email: str = None, name: str = None) -> str:
    """
    Busca un contacto por teléfono o email. Si no existe, lo crea.
    Detecta duplicados y devuelve el ID del contacto (entity_id).
    
    Args:
        phone: Número de teléfono del contacto.
        email: Email del contacto.
        name: Nombre del contacto (usado si se debe crear uno nuevo).
        
    Returns:
        str: El ID del contacto en Bitrix24.
    """
    contact_id = None
    
    # 1. Buscar por Teléfono
    if phone:
        # Normalizar teléfono si es necesario (simple strip por ahora)
        phone_clean = phone.strip()
        try:
            result = call_bitrix_method("crm.duplicate.findbycomm", {
                "type": "PHONE",
                "values": [phone_clean],
                "entity_type": "CONTACT"
            })
            if result.get("result"):
                # Tomamos el primer ID encontrado
                contact_id = result["result"][0]
                print(f"✅ Contacto encontrado por teléfono: {contact_id}")
        except Exception as e:
            print(f"Error searching by phone: {e}")

    # 2. Buscar por Email (si no se encontró por teléfono)
    if not contact_id and email:
        email_clean = email.strip()
        try:
            result = call_bitrix_method("crm.duplicate.findbycomm", {
                "type": "EMAIL",
                "values": [email_clean],
                "entity_type": "CONTACT"
            })
            if result.get("result"):
                contact_id = result["result"][0]
                print(f"✅ Contacto encontrado por email: {contact_id}")
        except Exception as e:
            print(f"Error searching by email: {e}")

    # 3. Si se encontró, retornamos ID. (Aquí podría ir lógica de merge si hay múltiples)
    if contact_id:
        return str(contact_id)

    # 4. Si no se encontró, crear contacto
    print("⚠️ Contacto no encontrado, creando uno nuevo...")
    fields = {
        "NAME": name or "Desconocido",
        "OPENED": "Y",
        "SOURCE_ID": "WEBFORM" # O similar
    }
    if phone:
        fields["PHONE"] = [{"VALUE": phone, "VALUE_TYPE": "WORK"}]
    if email:
        fields["EMAIL"] = [{"VALUE": email, "VALUE_TYPE": "WORK"}]
        
    try:
        result = call_bitrix_method("crm.contact.add", {"fields": fields})
        new_id = result.get("result")
        print(f"✅ Nuevo contacto creado: {new_id}")
        return str(new_id)
    except Exception as e:
        print(f"❌ Error al crear contacto: {e}")
        return "Error creating contact"
