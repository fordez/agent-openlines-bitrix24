import sys
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

def delete_bot(bot_id):
    print(f"Intentando eliminar bot con ID: {bot_id}...")
    
    try:
        payload = {"BOT_ID": bot_id}
        result = auth.call_bitrix_method("imbot.unregister", payload)
        
        if "result" in result and result["result"] is True:
            print(f"¡Bot {bot_id} eliminado exitosamente!")
        else:
            print("No se pudo eliminar el bot o respuesta inesperada.")
            print(result)

    except Exception as e:
        print(f"Error al eliminar el bot: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        bot_id = sys.argv[1]
        delete_bot(bot_id)
    else:
        print("Uso: python delete_bot.py <BOT_ID>")
        print("Ejemplo: python delete_bot.py 3238")
        print("\nPuedes ver los IDs de tus bots ejecutando: python get_bot_info.py")
