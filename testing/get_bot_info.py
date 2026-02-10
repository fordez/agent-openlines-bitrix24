import json
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

def get_bot_info():
    print("Obteniendo lista de bots registrados...")
    
    try:
        # Llamamos a imbot.bot.list para ver todos los bots registrados por esta app
        result = auth.call_bitrix_method("imbot.bot.list")
        
        if "result" in result:
            bots = result["result"]
            print(f"Se encontraron {len(bots)} bots registrados:")
            
            for bot_id, bot_data in bots.items():
                print("\n------------------------------------------------")
                print(f"ID: {bot_id}")
                print(f"CODE: {bot_data.get('CODE')}")
                print(f"TYPE: {bot_data.get('TYPE')}")
                print(f"EVENT_HANDLER: {bot_data.get('EVENT_HANDLER')}")
                print(f"OPENLINE: {bot_data.get('OPENLINE')}")
                
                # Imprimir propiedades si existen
                properties = bot_data.get('PROPERTIES', {})
                if properties:
                    print("PROPERTIES:")
                    for prop, value in properties.items():
                        print(f"  - {prop}: {value}")
                
                # Imprimir JSON completo para ver todos los campos
                print("DATA COMPLETA:")
                print(json.dumps(bot_data, indent=2))
                
                print("------------------------------------------------")
        else:
            print("No se encontraron bots o la estructura de respuesta es inesperada.")
            print(result)

    except Exception as e:
        print(f"Error al obtener información del bot: {e}")

if __name__ == "__main__":
    get_bot_info()
