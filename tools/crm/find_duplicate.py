"""
Herramienta para buscar duplicados por teléfono o email en Bitrix24.
Usa el método: crm.duplicate.findbycomm
"""
from app.auth import call_bitrix_method
import json


def find_duplicate(phone: str = None, email: str = None) -> str:
    """
    Usa esta tool para EVITAR DUPLICADOS verificando si ya existe un Lead/Contacto con ese teléfono/email.
    Usa esto antes de crear un Lead nuevo.
    
    Args:
        phone, email: Datos a verificar.
    """
    if not value:
        return "Error: value es requerido."
    
    comm_type = comm_type.upper()
    if comm_type not in ("PHONE", "EMAIL"):
        return "Error: comm_type debe ser 'PHONE' o 'EMAIL'."

    try:
        result = call_bitrix_method("crm.duplicate.findbycomm", {
            "type": comm_type,
            "values": [value.strip()],
            "entity_type": entity_type.upper()
        })
        
        found = result.get("result")
        if found:
            return json.dumps(found, ensure_ascii=False)
        else:
            return f"No se encontraron duplicados de tipo {entity_type} para {comm_type}={value}."
    except Exception as e:
        return f"Error buscando duplicados: {e}"
