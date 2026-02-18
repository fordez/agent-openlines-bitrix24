"""
Bot Viajes — Webhook de Bitrix24 con agente AI (Gemini via mcp-agent).
Punto de entrada principal del servidor FastAPI.
Usa fire-and-forget para no bloquear al recibir eventos concurrentes.
"""
from fastapi import FastAPI, Request
import uvicorn
import asyncio

from app.bitrix import BOT_ID, extract_event_data, send_reply
from app import agent

server = FastAPI(title="Bot Viajes", version="1.0.0")


@server.on_event("startup")
async def startup():
    """Inicializa servicios al arrancar."""
    from app.token_manager import get_token_manager
    from app.firestore_config import get_firestore_config
    from app.metrics import MetricsService
    
    # Init tokens
    await get_token_manager()
    print("🚀 TokenManager inicializado")
    
    # Init Firestore and Start Listener
    fs_service = await get_firestore_config()
    fs_service.start_listener()
    print("🔥 Firestore Listener iniciado")

    # Start System Metrics
    metrics = await MetricsService.get_instance()
    await metrics.start_system_metrics_logger()
    print("📊 System Metrics Logger iniciado")


@server.post("/")
async def bitrix_webhook(request: Request):
    """
    Endpoint para recibir eventos de Bitrix24.
    Responde 200 OK INMEDIATAMENTE y procesa en background.
    Esto evita timeouts de Bitrix y permite concurrencia total.
    """
    # Leer datos del evento
    try:
        form_data = await request.form()
        data = dict(form_data)
        event = data.get("event")
    except Exception:
        data = {}
        event = None

    # Fallback: body raw
    if not data:
        try:
            body = await request.body()
            body_str = body.decode("utf-8")
            if body_str:
                import urllib.parse
                parsed = urllib.parse.parse_qs(body_str)
                data = {k: v[0] for k, v in parsed.items()}
                event = data.get("event")
        except Exception as e:
            print(f"Error parsing body: {e}")

    print(f"\n----- EVENTO BITRIX24: {event or 'DESCONOCIDO'} -----")

    # Fire-and-forget: procesar en background, responder inmediato
    if event == "ONIMBOTMESSAGEADD":
        asyncio.create_task(_safe_handle_message(data))

    else:
        print(f"  ℹ️ Evento no procesado: {event}")

    return {"status": "ok"}


async def _safe_handle_message(data: dict):
    """Wrapper seguro para handle_message en background."""
    try:
        await handle_message(data)
    except Exception as e:
        print(f"  ❌ Error en background handle_message: {e}")
        import traceback
        traceback.print_exc()


async def _safe_handle_join(data: dict):
    """Wrapper seguro para handle_join en background."""
    try:
        await handle_join(data)
    except Exception as e:
        print(f"  ❌ Error en background handle_join: {e}")


async def handle_message(data: dict):
    """Procesa un mensaje entrante: consulta Gemini y responde."""
    extracted = extract_event_data(data)
    print(f"  🔍 Extracted: {extracted}")

    dialog_id = extracted.get("DIALOG_ID")
    chat_id = extracted.get("CHAT_ID")
    message = extracted.get("MESSAGE")
    from_user_id = extracted.get("FROM_USER_ID")
    user_name = extracted.get("USER_NAME", "Desconocido")
    # Token del EVENTO para responder a Bitrix (no para tools)
    event_token = extracted.get("BOT_access_token")
    client_endpoint = extracted.get("BOT_client_endpoint")
    session_id = extracted.get("SESSION_ID")

    # Ignorar mensajes del propio bot
    if from_user_id == BOT_ID:
        print("  ⏭️ Mensaje del propio bot, ignorando.")
        return

    print(f"  💬 De: {user_name} (ID: {from_user_id})")
    print(f"  📝 Mensaje: {message}")
    print(f"  🆔 Dialog: {dialog_id}")

    if not dialog_id or not message:
        print("  ⚠️ Faltan DIALOG_ID o MESSAGE en el evento.")
        return

    # Guardar dominio y member_id (las tools usan TokenManager, no este token)
    import os
    if client_endpoint:
        domain = client_endpoint.replace("https://", "").split("/")[0]
        os.environ["BITRIX_DOMAIN"] = domain
        os.environ["BITRIX_CLIENT_ENDPOINT"] = client_endpoint
    
    # Extraer member_id del evento para identificar al tenant
    auth_member_id = extracted.get("AUTH_member_id") or extracted.get("member_id")
    if auth_member_id:
        os.environ["BITRIX_MEMBER_ID"] = auth_member_id
        from app.context_vars import member_id_var
        member_id_var.set(auth_member_id)
        
        # Guardar mapeo chat_id -> member_id en Redis para que las tools puedan recuperarlo
        if chat_id:
            from app.redis_client import get_redis
            r = await get_redis()
            await r.set(f"map:chat_to_member:{chat_id}", auth_member_id, ex=3600*24)

    # Consultar LLM (tools usan TokenManager internamente)
    provider = os.getenv("LLM_PROVIDER", "unknown")
    print(f"  🤖 Consultando AI ({provider})...")
    ai_response = await agent.get_response(
        message, 
        dialog_id, 
        # Tools NO necesitan token (usan TokenManager)
        # Typing indicator SÍ necesita token del evento
        event_token=event_token,
        client_endpoint=client_endpoint, 
        session_id=session_id,
        chat_id_num=chat_id,  # CORREGIDO: Usar el nombre de argumento correcto
        user_name=user_name,
        user_id=from_user_id
    )
    print(f"  💡 Respuesta: {ai_response[:100]}...")

    # Responder a Bitrix (USA token del evento, no TokenManager)
    await send_reply(event_token, client_endpoint, dialog_id, ai_response, chat_id=chat_id, session_id=session_id)
    print("------------------------------------\n")


async def handle_join(data: dict):
    """Envía mensaje de bienvenida cuando el bot se une al chat."""
    extracted = extract_event_data(data)
    dialog_id = extracted.get("DIALOG_ID")
    access_token = extracted.get("BOT_access_token")
    client_endpoint = extracted.get("BOT_client_endpoint")

    print(f"  🤝 Bot se unió al chat: {dialog_id}")

    if dialog_id and access_token and client_endpoint:
        welcome = "¡Hola! 👋 Soy Bot Viajes (ID: 3040), tu asistente virtual. ¿En qué puedo ayudarte hoy?"
        await send_reply(access_token, client_endpoint, dialog_id, welcome)


if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8080)
