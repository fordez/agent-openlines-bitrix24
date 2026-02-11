from app.auth import call_bitrix_method
import sys

async def session_title_update(chat_id: int, title: str, access_token: str = None, domain: str = None) -> str:
    """
    Actualiza el título de un chat en Bitrix24.
    Útil para poner un nombre descriptivo a la conversación de OpenLines (ej: 'Vuelo a China - Jairo').
    
    Args:
        chat_id: ID del chat (no el DIALOG_ID, sino el ID numérico).
        title: El nuevo título para el chat.
    """
    sys.stderr.write(f"  📝 Tool session_title_update: chat_id={chat_id}, title={title}\n")

    if not chat_id:
        return "Error: chat_id es requerido."
    if not title:
        return "Error: title es requerido."

    try:
        params = {
            "CHAT_ID": chat_id,
            "TITLE": title
        }

        result = await call_bitrix_method("im.chat.updateTitle", params, access_token=access_token, domain=domain)
        
        if result.get("result"):
            return f"Título del chat {chat_id} actualizado a '{title}' correctamente."
        else:
            error = result.get("error_description", result)
            return f"Error al actualizar el título del chat: {error}"

    except Exception as e:
        return f"Error técnico al actualizar el título del chat: {e}"
