import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app import auth

load_dotenv()

BOT_CODE = os.getenv("BOT_CODE", "bot_viajes")

def send_message(dialog_id, message):
    if not message:
        print("❌ Error: El mensaje no puede estar vacío.")
        return

    print(f"Enviando mensaje al diálogo {dialog_id}...")
    
    # Primero necesitamos el ID numérico del bot, si no está en ENV, lo buscamos
    # Podríamos guardarlo en .env para ahorrar llamadas, pero por ahora lo buscamos.
    try:
        # Intentar obtener ID del bot
        bots_result = auth.call_bitrix_method("imbot.bot.list")
        bot_id = None
        
        if "result" in bots_result:
             for bid, bdata in bots_result["result"].items():
                 if bdata.get("CODE") == BOT_CODE:
                     bot_id = bid
                     break
        
        if not bot_id:
            print(f"❌ Error: No se encontró el bot con código {BOT_CODE}.")
            return

        payload = {
            "BOT_ID": bot_id, 
            "DIALOG_ID": dialog_id,
            "MESSAGE": message
        }

        result = auth.call_bitrix_method("imbot.message.add", payload)
        
        if "result" in result:
             print(f"✅ Mensaje enviado exitosamente. ID Mensaje: {result['result']}")
        else:
             print(f"⚠️ Error enviando mensaje:")
             print(result)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python send_message.py <DIALOG_ID> <MENSAJE>")
        print("Ejemplo: python send_message.py chat123 'Hola mundo'")
        sys.exit(1)
        
    dialog_id = sys.argv[1]
    message = sys.argv[2]
    
    send_message(dialog_id, message)
