"""
Herramienta para enviar un mensaje en una sesión de Open Lines.
Usa el método: imopenlines.bot.session.message.send
"""
from app.auth import call_bitrix_method


def session_send_message(chat_id: int, message: str) -> str:
    """
    Usa esta tool para ENVIAR MENSAJES al cliente por el canal abierto (WhatsApp/Web).
    Úsalo para responder preguntas o confirmar acciones.
    
    Args:
        chat_id: ID del chat activo.
        message: Texto del mensaje a enviar.

    Returns:
        str: Mensaje de éxito o error.
    """
    if not chat_id:
        return "Error: chat_id es requerido."
    if not message:
        return "Error: message es requerido."

    params = {
        "CHAT_ID": chat_id,
        "MESSAGE": message,
    }
    if name:
        params["NAME"] = name

    try:
        result = call_bitrix_method("imopenlines.bot.session.message.send", params)
        if result.get("result"):
            return f"Mensaje enviado exitosamente en chat {chat_id}."
        else:
            error = result.get("error_description", result)
            return f"Error enviando mensaje: {error}"
    except Exception as e:
        return f"Error enviando mensaje en sesión: {e}"
