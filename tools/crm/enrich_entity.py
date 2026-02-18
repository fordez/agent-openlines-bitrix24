from app.auth import call_bitrix_method
from app.models import EnrichmentRequest
import sys

async def enrich_entity(entity_id: int, entity_type: str, fields: dict) -> str:
    """
    Enriquece o actualiza cualquier entidad del CRM (LEAD, CONTACT, DEAL, COMPANY) 
    con datos adicionales (origen, comentarios, campos personalizados).
    """
    # Usamos Pydantic para validar internamente si llega como dict
    try:
        req = EnrichmentRequest(entity_id=entity_id, entity_type=entity_type, fields=fields)
    except Exception as e:
        return f"Error de validación: {e}"

    entity_type = req.entity_type.upper()
    bitrix_method = f"crm.{entity_type.lower()}.update"
    
    # Extraemos los campos (incluyendo los 'extra' de Pydantic)
    raw_fields = req.fields.model_dump(exclude_unset=True)
    raw_fields.update(req.fields.model_extra or {})

    normalized_fields = {}
    for k, v in raw_fields.items():
        k_upper = k.upper()
        
        # Manejo especial para multivampos (PHONE, EMAIL)
        if entity_type in ["LEAD", "CONTACT"] and k_upper in ["PHONE", "EMAIL"]:
            if isinstance(v, str):
                normalized_fields[k_upper] = [{"VALUE": v, "VALUE_TYPE": "WORK"}]
            else:
                normalized_fields[k_upper] = v
        else:
            normalized_fields[k_upper] = v

    if entity_type == "LEAD" and "SOURCE_ID" not in normalized_fields:
        normalized_fields["SOURCE_ID"] = "WEB"

    sys.stderr.write(f"  🧠 Pydantic-Enriched {entity_type}:{req.entity_id} with {normalized_fields}\n")

    try:
        result = await call_bitrix_method(bitrix_method, {
            "id": req.entity_id,
            "fields": normalized_fields
        })
        
        if result.get("result"):
            return f"{entity_type} {req.entity_id} enriquecido exitosamente."
        else:
            error = result.get("error_description", result)
            return f"Error enriqueciendo {entity_type}: {error}"
            
    except Exception as e:
        sys.stderr.write(f"  ❌ Error in enrich_entity: {e}\n")
        return f"Excepción en enrich_entity: {e}"
