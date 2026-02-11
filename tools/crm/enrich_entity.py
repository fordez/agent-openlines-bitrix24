"""
Tool for intelligent CRM entity enrichment in Bitrix24.
Supports Lead, Contact, Deal, and Company updates with nested fields.
"""
from app.auth import call_bitrix_method
import json
import sys

async def enrich_entity(entity_id: int, entity_type: str, fields: dict) -> str:
    """
    Enriquece o actualiza cualquier entidad del CRM (LEAD, CONTACT, DEAL, COMPANY) 
    con datos adicionales (origen, comentarios, campos personalizados).
    
    Args:
        entity_id: ID de la entidad a actualizar.
        entity_type: Tipo de entidad (LEAD, CONTACT, DEAL, COMPANY).
        fields: Diccionario con los campos a actualizar.
    """
    if not entity_id or not entity_type:
        return "Error: entity_id y entity_type son requeridos."

    if isinstance(fields, str):
        try:
            fields = json.loads(fields)
        except Exception:
            return "Error: fields debe ser un JSON válido o diccionario."

    if not fields:
        return "Error: no se proporcionaron campos para enriquecer."

    # Normalización básica de campos y tipos
    entity_type = entity_type.upper()
    bitrix_method = f"crm.{entity_type.lower()}.update"
    
    # Mapeo de campos comunes y normalización
    normalized_fields = {}
    for k, v in fields.items():
        k_upper = k.upper()
        
        # Manejo especial para multivampos (PHONE, EMAIL) en Leads y Contactos
        if entity_type in ["LEAD", "CONTACT"] and k_upper in ["PHONE", "EMAIL"]:
            if isinstance(v, str):
                normalized_fields[k_upper] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
            elif isinstance(v, list):
                normalized_fields[k_upper] = v
            else:
                normalized_fields[k_upper] = v
        else:
            normalized_fields[k_upper] = v

    # Forzar SOURCE_ID si se trata de un Lead y no viene especificado
    if entity_type == "LEAD" and "SOURCE_ID" not in normalized_fields:
        normalized_fields["SOURCE_ID"] = "WEB" # Valor por defecto para el bot

    sys.stderr.write(f"  🧠 Enriching {entity_type}:{entity_id} with {normalized_fields}\n")

    try:
        result = await call_bitrix_method(bitrix_method, {
            "id": entity_id,
            "fields": normalized_fields
        })
        
        if result.get("result"):
            return f"{entity_type} {entity_id} enriquecido exitosamente."
        else:
            error = result.get("error_description", result)
            return f"Error enriqueciendo {entity_type}: {error}"
            
    except Exception as e:
        sys.stderr.write(f"  ❌ Error in enrich_entity: {e}\n")
        return f"Excepción en enrich_entity: {e}"
