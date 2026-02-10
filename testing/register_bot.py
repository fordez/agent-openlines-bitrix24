import os
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

BOT_CODE = os.getenv("BOT_CODE", "bot_viajes")
BOT_NAME = os.getenv("BOT_NAME", "Bot Viajes")
WEBHOOK_HANDLER_URL = os.getenv("WEBHOOK_HANDLER_URL")

def register_bot():
    if not WEBHOOK_HANDLER_URL or "tu-url-ngrok" in WEBHOOK_HANDLER_URL:
        print("ERROR: Por favor configura WEBHOOK_HANDLER_URL en el archivo .env con tu URL de ngrok")
        return

    print(f"Registrando bot '{BOT_NAME}'...")
    
    payload = {
        "CODE": BOT_CODE,
        "TYPE": "O",  # Open Lines
        "EVENT_HANDLER": WEBHOOK_HANDLER_URL,
        "OPENLINE": "Y",
        "PROPERTIES": {
            "NAME": BOT_NAME,
            "WORK_POSITION": "Asistente Virtual"
        }
    }

    try:
        result = auth.call_bitrix_method("imbot.register", payload)
        
        if "error" in result:
            print(f"Error de Bitrix24: {result['error_description']}")
        else:
            print(f"¡Bot registrado exitosamente! ID: {result['result']}")
            
    except Exception as e:
        print(f"Fallo el registro del bot: {e}")

if __name__ == "__main__":
    register_bot()
