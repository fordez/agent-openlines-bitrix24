import os
from dotenv import load_dotenv
from app import auth

load_dotenv()

WEBHOOK_HANDLER_URL = os.getenv("WEBHOOK_HANDLER_URL")

def bind_event():
    if not WEBHOOK_HANDLER_URL:
        print("WEBHOOK_HANDLER_URL no definido en .env")
        return

    print(f"Vinculando evento ONIMBOTMESSAGEADD a {WEBHOOK_HANDLER_URL}...")
    
    # Intentar vincular el evento globlamente para la aplicación
    payload = {
        "event": "ONIMBOTMESSAGEADD",
        "handler": WEBHOOK_HANDLER_URL,
        "auth_type": 0 # 0 = user, but for local app it might be different. Let's try default.
    }
    
    try:
        result = auth.call_bitrix_method("event.bind", payload)
        print(f"Resultado event.bind: {result}")
    except Exception as e:
        print(f"Error en event.bind: {e}")

if __name__ == "__main__":
    bind_event()
