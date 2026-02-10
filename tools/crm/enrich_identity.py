"""
Herramienta para enriquecer datos de contacto en Bitrix24.
"""
from app.auth import call_bitrix_method
import json

def enrich_identity(entity_id: str, fields: dict) -> str:
    """
    Completa o actualiza datos del contacto sin sobrescribir información válida si ya existe (opcional),
    o simplemente actualiza los campos proporcionados.
    
    Args:
        entity_id: ID del contacto en Bitrix24.
        fields: Diccionario con campos a actualizar (ej: {"NAME": "Juan", "COMMENTS": "..."}).
    
    Returns:
        str: Mensaje de éxito o error.
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
        call_bitrix_method("crm.contact.update", {
            "id": entity_id,
            "fields": bitrix_fields
        })
        return f"Contacto {entity_id} actualizado exitosamente."
    except Exception as e:
        return f"Error actualizando contacto: {e}"
