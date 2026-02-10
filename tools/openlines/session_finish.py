"""
Herramienta para finalizar una sesión de Open Lines.
Usa el método: imopenlines.bot.session.finish
"""
from app.auth import call_bitrix_method


async def session_finish(chat_id: str) -> str:
    """
    Finaliza/cierra la sesión del bot en un chat de Open Lines.
    Esto marca la conversación como terminada.

    Args:
        chat_id: ID del chat de Open Lines a finalizar.

    Returns:
        str: Mensaje de éxito o error.
    """
    if not chat_id:
        return "Error: chat_id es requerido."

    try:
        result = await call_bitrix_method("imopenlines.bot.session.finish", {
            "CHAT_ID": chat_id,
        })
        if result.get("result"):
            return f"Sesión del chat {chat_id} finalizada exitosamente."
        else:
            error = result.get("error_description", result)
            return f"Error al finalizar sesión: {error}"
    except Exception as e:
        return f"Error al finalizar sesión: {e}"
