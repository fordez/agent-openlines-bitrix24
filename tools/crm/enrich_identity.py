"""
Herramienta para enriquecer datos de contacto en Bitrix24.
"""
from app.auth import call_bitrix_method
import json

async def enrich_identity(name: str = None, phone: str = None, email: str = None) -> str:
    """
    Usa esta tool al INICIO para buscar si el contacto ya existe en la base de datos (Leads/Contactos).
    Ayuda a retomar conversaciones pasadas.
    
    Args:
        name, phone, email: Datos para buscar coincidencias.
    """
    if not entity_id:
        return "Falta entity_id"

    # Podríamos leer primero el contacto para ver qué campos están vacíos si quisiéramos ser muy estrictos
    # con "no sobrescribir". Por ahora, asumiremos que el agente envía info nueva/mejor.
    
    # Mapeo de campos simples para facilitar al LLM
    # El LLM puede enviar keys en minúscula, las pasamos a Bitrix UPPERCASE
    bitrix_fields = {}
    
    # Si fields viene como string json
    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except:
             return "Error: fields must be a dict or valid json string"

    for k, v in fields.items():
        k_upper = k.upper()
        if k_upper in ["NAME", "LAST_NAME", "SECOND_NAME", "COMMENTS", "SOURCE_DESCRIPTION"]:
            bitrix_fields[k_upper] = v
        elif k_upper == "PHONE":
             bitrix_fields["PHONE"] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
        elif k_upper == "EMAIL":
             bitrix_fields["EMAIL"] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
        else:
            # Campos personalizados u otros
            bitrix_fields[k_upper] = v
            
    try:
        await call_bitrix_method("crm.contact.update", {
            "id": entity_id,
            "fields": bitrix_fields
        })
        return f"Contacto {entity_id} actualizado exitosamente."
    except Exception as e:
        return f"Error actualizando contacto: {e}"
