"""
Módulo de utilidades para Bitrix24: parseo de eventos y envío de respuestas.
Usa httpx async para no bloquear el event loop.
"""
import httpx


BOT_ID = "3242"


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

    # Campos de BOT (token, etc.) - buscar por BOT_ID
    bot_prefix = f"data[BOT][{BOT_ID}]"
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

    return result


async def send_reply(access_token: str, client_endpoint: str, dialog_id: str, message: str, chat_id: str = None):
    """
    Envía un mensaje de respuesta al chat de Bitrix24 de forma asíncrona.
    """
    url = f"{client_endpoint}imbot.message.add"
    payload = {
        "BOT_ID": BOT_ID,
        "DIALOG_ID": dialog_id,
        "MESSAGE": message,
        "auth": access_token,
    }

    if chat_id:
        payload["CHAT_ID"] = chat_id

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, json=payload)
            result = response.json()
            if "result" in result:
                print(f"  ✅ Respuesta enviada al chat {dialog_id} (msg_id: {result['result']})")
            else:
                print(f"  ⚠️ Error al enviar respuesta: {result}")
    except Exception as e:
        print(f"  ❌ Error HTTP al enviar respuesta: {e}")
