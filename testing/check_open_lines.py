import json
import sys
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

def check_open_lines(target_bot_id=None):
    print("Obteniendo configuraciones de Canales Abiertos (imopenlines.config.list.get)...")
    
    try:
        result = auth.call_bitrix_method("imopenlines.config.list.get")
        
        if "result" in result:
            configs = result["result"]
            print(f"Se encontraron {len(configs)} líneas abiertas configuradas:")
            
            found_connection = False
            
            for config in configs:
                line_id = config.get("ID")
                line_name = config.get("LINE_NAME")
                bot_id = config.get("BOT_ID") or config.get("WELCOME_BOT_ID")
                bot_code = config.get("BOT_CODE")
                
                # Check enable status
                is_enabled = config.get("WELCOME_BOT_ENABLE") == "Y"
                if not is_enabled and bot_id:
                     bot_id = f"{bot_id} (Disabled)"
                
                print("\n------------------------------------------------")
                print(f"ID Línea: {line_id}")
                print(f"Nombre: {line_name}")
                print(f"Bot Asignado (ID): {bot_id}")
                print(f"Bot Asignado (Code): {bot_code}")
                

                
                if target_bot_id and str(bot_id) == str(target_bot_id):
                    print(f"¡ENCONTRADO! El bot {target_bot_id} está conectado a esta línea.")
                    found_connection = True
                
                print("------------------------------------------------")
            
            if target_bot_id:
                if found_connection:
                    print(f"\n✅ El bot {target_bot_id} está correctamente asignado a al menos una línea.")
                else:
                    print(f"\n❌ El bot {target_bot_id} NO está asignado a ninguna línea abierta visible.")
                    print("Debes ir a Bitrix24 -> Contact Center -> Tu Canal -> Configuración -> Chat Bots y seleccionarlo.")
                    
        else:
            print("No se encontraron configuraciones o respuesta inesperada.")
            print(result)

    except Exception as e:
        print(f"Error al obtener líneas abiertas: {e}")

if __name__ == "__main__":
    target_id = None
    if len(sys.argv) > 1:
        target_id = sys.argv[1]
    
    check_open_lines(target_id)
