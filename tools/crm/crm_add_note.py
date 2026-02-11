"""
Herramienta para añadir comentarios a la línea de tiempo (timeline) de cualquier entidad CRM en Bitrix24.
Usa el método: crm.timeline.comment.add
"""
from app.auth import call_bitrix_method
import sys

async def crm_add_note(entity_id: int, entity_type: str, message: str, access_token: str = None, domain: str = None) -> str:
    """
    Agrega una nota o comentario a la ficha de un Lead, Contacto o Negocio.
    Úsalo para registrar descubrimientos, preferencias o resumen de llamadas.

    Args:
        entity_id: ID de la entidad CRM.
        entity_type: Tipo de entidad (LEAD, CONTACT, DEAL).
        message: Texto de la nota a agregar.
    """
    if not entity_id or not entity_type or not message:
        return "Error: entity_id, entity_type y message son requeridos."

    # Normalizar entity_type (Bitrix suele esperar minúsculas o IDs numéricos, pero el SDK REST acepta strings)
    entity_type_map = {
        "LEAD": "lead",
        "CONTACT": "contact",
        "DEAL": "deal",
        "COMPANY": "company"
    }
    
    e_type = entity_type_map.get(entity_type.upper(), entity_type.lower())

    sys.stderr.write(f"  📝 Tool crm_add_note: {e_type}:{entity_id}\n")

    try:
        params = {
            "fields": {
                "ENTITY_ID": entity_id,
                "ENTITY_TYPE": e_type,
                "COMMENT": message
            }
        }

        result = await call_bitrix_method("crm.timeline.comment.add", params, access_token=access_token, domain=domain)
        
        if result.get("result"):
            return f"Nota agregada exitosamente a {entity_type} {entity_id}."
        else:
            error = result.get("error_description", result)
            sys.stderr.write(f"  ❌ Error en crm.timeline.comment.add: {error}\n")
            return f"Error al agregar nota: {error}"

    except Exception as e:
        sys.stderr.write(f"  ❌ Excepción en crm_add_note: {e}\n")
        return f"Error al agregar nota: {e}"
