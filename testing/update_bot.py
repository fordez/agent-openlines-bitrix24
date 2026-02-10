import os
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import auth

# Cargar variables de entorno
load_dotenv()

BOT_CODE = os.getenv("BOT_CODE", "bot_viajes")
BOT_NAME = os.getenv("BOT_NAME", "Bot Viajes")
WEBHOOK_HANDLER_URL = os.getenv("WEBHOOK_HANDLER_URL")

def update_bot():
    if not WEBHOOK_HANDLER_URL or "tu-url-ngrok" in WEBHOOK_HANDLER_URL:
        print("ERROR: Por favor configura WEBHOOK_HANDLER_URL en el archivo .env")
        return

    # Obtener ID del bot primero
    print(f"Buscando bot '{BOT_CODE}'...")
    try:
        bots_result = auth.call_bitrix_method("imbot.bot.list")
        bot_id = None
        
        if "result" in bots_result:
             for bid, bdata in bots_result["result"].items():
                 if bdata.get("CODE") == BOT_CODE:
                     bot_id = bid
                     break
        
        if not bot_id:
            print(f"No se encontró el bot con código {BOT_CODE}. Registralo primero.")
            return

        print(f"Bot encontrado con ID: {bot_id}. Actualizando URL a: {WEBHOOK_HANDLER_URL}")

        # Para imbot.update, los campos a actualizar van dentro de FIELDS
        payload = {
            "BOT_ID": bot_id,
            "FIELDS": {
                "EVENT_HANDLER": WEBHOOK_HANDLER_URL,
                "PROPERTIES": {
                    "NAME": BOT_NAME,
                    "WORK_POSITION": "Asistente Virtual"
                }
            }
        }

        result = auth.call_bitrix_method("imbot.update", payload)
        
        if "result" in result and result["result"]:
            print("¡Bot actualizado exitosamente!")
        else:
            print("Error al actualizar bot o respuesta inesperada.")
            print(result)

    except Exception as e:
        print(f"Error al actualizar el bot: {e}")

if __name__ == "__main__":
    update_bot()
