from app.auth import call_bitrix_method
import sys

async def session_crm_bind(chat_id: int, entity_id: int = None, entity_type: str = "LEAD", access_token: str = None, domain: str = None) -> str:
    """
    Vincula el chat actual a una entidad CRM (Lead/Deal) registrando la información en el Timeline.
    Nota: La vinculación visual manual vía REST no está soportada en este entorno; el sistema lo gestiona automáticamente.
    """
    sys.stderr.write(f"  🔗 Tool session_crm_bind: chat_id={chat_id}, entity={entity_type}:{entity_id}\n")

    if not entity_id:
        return "Error: Se requiere entity_id para vincular."

    try:
        # Intentamos el vínculo visual y estructural mediante im.chat.setEntity
        from app.auth import call_bitrix_method
        
        bind_params = {
            "CHAT_ID": chat_id,
            "ENTITY_TYPE": entity_type.upper(),
            "ENTITY_ID": entity_id
        }
        
        sys.stderr.write(f"  📡 Ejecutando im.chat.setEntity para {entity_type}:{entity_id} en chat {chat_id}\n")
        
        result = {}
        try:
            result = await call_bitrix_method("im.chat.setEntity", bind_params)
        except Exception as e:
            sys.stderr.write(f"  ⚠️ Warning: im.chat.setEntity falló (posiblemente no soportado): {e}\n")
        
        # También dejamos una nota en el CRM Timeline para trazabilidad
        from tools.crm.crm_add_note import crm_add_note
        await crm_add_note(entity_id=entity_id, entity_type=entity_type, message=f"[BOT] Conversación {chat_id} vinculada formalmente a esta ficha.")
        
        if result.get("result"):
            return f"Chat {chat_id} vinculado exitosamente a {entity_type} {entity_id}."
        else:
            return f"El chat {chat_id} ahora se referencia en la ficha de {entity_type} {entity_id}, aunque la API retornó un estado inesperado."

    except Exception as e:
        sys.stderr.write(f"  ❌ Error en session_crm_bind: {e}\n")
        return f"Error ejecutando vínculo CRM: {e}"
