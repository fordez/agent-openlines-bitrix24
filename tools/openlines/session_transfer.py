"""
Herramienta para transferir una sesión de Open Lines a un operador o cola.
Usa el método: imopenlines.bot.session.transfer
"""
from app.auth import call_bitrix_method


async def session_transfer(chat_id: str, user_id: str = "", queue_id: str = "", access_token: str = None, domain: str = None) -> str:
    """
    Usa esta tool para TRANSFERIR la conversación a un HUMANO cuando la situación se complique o el cliente pida hablar con alguien.
    
    Args:
        chat_id: ID del chat.
        user_id: ID del agente humano (Opcional, si no se da se enviará a cola).
        queue_id: ID de la cola/línea abierta destino (Opcional, si no se da se enviará a un agente específico).
        access_token: Token de acceso de Bitrix24.
        domain: Dominio de Bitrix24.
    """
    if not chat_id:
        return "Error: chat_id es requerido."
    if not user_id and not queue_id:
        import sys
        sys.stderr.write(f"  ⚠️ No se proporcionó user_id ni queue_id para chat {chat_id}. Usando queue_id=1 por defecto.\n")
        queue_id = "1"

    params = {"CHAT_ID": chat_id}
    if user_id:
        params["USER_ID"] = user_id
    if queue_id:
        params["QUEUE_ID"] = queue_id

    try:
        import sys
        sys.stderr.write(f"  📤 Intentando transferencia: CHAT={chat_id}, USER={user_id}, QUEUE={queue_id}\n")
        result = await call_bitrix_method("imopenlines.bot.session.transfer", params, access_token=access_token, domain=domain)
        if result.get("result"):
            dest = f"operador {user_id}" if user_id else f"cola {queue_id}"
            return f"Sesión del chat {chat_id} transferida exitosamente a {dest}."
        else:
            error = result.get("error_description", result)
            return f"Error al transferir sesión: {error}"
    except Exception as e:
        return f"Error al transferir sesión: {e}"
