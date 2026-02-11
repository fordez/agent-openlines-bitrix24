"""
Módulo de utilidades para Bitrix24: parseo de eventos y envío de respuestas.
Usa httpx async para no bloquear el event loop.
"""
import httpx


import os

# ID del Bot (se puede sobreescribir con environment variable)
BOT_ID = os.getenv("BOT_ID", "3242")


def extract_event_data(data: dict) -> dict:
    """
    Extrae los campos relevantes del evento aplanado de Bitrix24.
    Las claves vienen en formato: data[PARAMS][FIELD], data[BOT][ID][FIELD], etc.
    """
    result = {}

    # Campos de PARAMS
    params_prefix = "data[PARAMS]"
    for key, value in data.items():
        if key.startswith(params_prefix):
            field = key[len(params_prefix) + 1:-1]
            result[field] = value

    # Detectar BOT_ID dinámicamente buscando en las claves de data
    detected_bot_id = None
    for key in data.keys():
        if key.startswith("data[BOT][") and "]" in key:
            # key es algo como 'data[BOT][3242][TOKEN]'
            parts = key.split("[")
            if len(parts) > 2:
                detected_bot_id = parts[2].split("]")[0]
                break
    
    bot_id = detected_bot_id or BOT_ID
    result["BOT_ID"] = bot_id

    # Campos de BOT (token, etc.) - buscar por bot_id
    bot_prefix = f"data[BOT][{bot_id}]"
    for key, value in data.items():
        if key.startswith(bot_prefix):
            rest = key[len(bot_prefix):]
            if rest.startswith("[") and rest.endswith("]"):
                field = rest[1:-1]
                result[f"BOT_{field}"] = value

    # Campos de USER
    user_prefix = "data[USER]"
    for key, value in data.items():
        if key.startswith(user_prefix):
            field = key[len(user_prefix) + 1:-1]
            result[f"USER_{field}"] = value

    # Auth del evento raíz
    auth_prefix = "auth["
    for key, value in data.items():
        if key.startswith(auth_prefix):
            field = key[len(auth_prefix):-1]
            result[f"AUTH_{field}"] = value

    # Búsqueda de respaldo para SESSION_ID y CHAT_ID en el nivel superior y CHAT_ENTITY_DATA_1
    for key, value in data.items():
        k_upper = key.upper()
        if "SESSION_ID" in k_upper and "SESSION_ID" not in result:
            result["SESSION_ID"] = value
        if "DIALOG_ID" in k_upper and "DIALOG_ID" not in result:
            result["DIALOG_ID"] = value
        if "CHAT_ID" in k_upper and "CHAT_ID" not in result:
             result["CHAT_ID"] = value

    # Si es OpenLines, intentar extraer SESSION_ID de CHAT_ENTITY_DATA_1 (formato: N|NONE|0|N|N|SESSION_ID|...)
    if result.get("CHAT_ENTITY_TYPE") == "LINES" and not result.get("SESSION_ID"):
        entity_data = result.get("CHAT_ENTITY_DATA_1", "")
        if entity_data:
            parts = entity_data.split("|")
            if len(parts) > 5 and parts[5].isdigit():
                result["SESSION_ID"] = int(parts[5])

    return result


async def send_reply(access_token: str, client_endpoint: str, dialog_id: str, message: str, chat_id: str = None, session_id: int = None):
    """
    Envía un mensaje de respuesta al chat de Bitrix24.
    Implementa un intento dual para asegurar visibilidad en OpenLines.
    """
    success = False
    
    # Intento 1: imbot.message.add (El más estándar para bots, suele ser el visible en el chat)
    url_im = f"{client_endpoint}imbot.message.add"
    payload_im = {
        "DIALOG_ID": dialog_id,
        "MESSAGE": message,
        "auth": access_token,
    }
    if BOT_ID: payload_im["BOT_ID"] = BOT_ID

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            res = await client.post(url_im, json=payload_im)
            data = res.json()
            if data.get("result"):
                print(f"  ✅ Msg enviado via imbot.message.add (Dialog: {dialog_id}, MsgID: {data['result']})")
                success = True
            else:
                print(f"  ⚠️ Fallo imbot.message.add: {data}")
    except Exception as e:
        print(f"  ❌ Error HTTP imbot: {e}")

    # Intento 2: imopenlines.bot.session.message.send (Específico para OpenLines, marca sesión como respondida)
    if session_id:
        url_ol = f"{client_endpoint}imopenlines.bot.session.message.send"
        payload_ol = {
            "SESSION_ID": session_id,
            "MESSAGE": message,
            "auth": access_token,
        }
        if chat_id: payload_ol["CHAT_ID"] = chat_id
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                res = await client.post(url_ol, json=payload_ol)
                data = res.json()
                if data.get("result"):
                    print(f"  ✅ Msg enviado via OpenLines (Session: {session_id}, Result: {data['result']})")
                    success = True
                else:
                    print(f"  ⚠️ Fallo OpenLines: {data}")
        except Exception as e:
            print(f"  ❌ Error HTTP OpenLines: {e}")

    return success

async def send_typing_indicator(access_token: str, client_endpoint: str, dialog_id: str, status: str = "on"):
    """
    Indica que el bot está escribiendo (on) o ha terminado (off).
    """
    url = f"{client_endpoint}imbot.chat.answer.typing"
    payload = {
        "BOT_ID": BOT_ID,
        "DIALOG_ID": dialog_id,
        "STATUS": status.upper(),
        "auth": access_token,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json=payload)
    except Exception as e:
        print(f"  ⚠️ Error al enviar typing indicator ({status}): {e}")
