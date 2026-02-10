import os
import sys
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

BOT_CODE = os.getenv("BOT_CODE", "bot_viajes")

def bind_bot_to_lines(target_lines=[64, 66]):
    print(f"Buscando bot '{BOT_CODE}' para vincularlo a las líneas: {target_lines}...")
    
    # 1. Obtener ID del bot
    try:
        bots_result = auth.call_bitrix_method("imbot.bot.list")
        bot_id = None
        
        if "result" in bots_result:
             for bid, bdata in bots_result["result"].items():
                 if bdata.get("CODE") == BOT_CODE:
                     bot_id = bid
                     break
        
        if not bot_id:
            print(f"❌ Error: No se encontró el bot con código {BOT_CODE}. Registralo primero.")
            return

        print(f"✅ Bot encontrado con ID: {bot_id}")

        # 2. Iterar sobre las líneas y asignar el bot
        for line_id in target_lines:
            print(f"\nIntentando asignar Bot ID {bot_id} a la Línea {line_id}...")
            
            # payload para imopenlines.config.update
            # https://training.bitrix24.com/rest_help/imopenlines/config/imopenlines_config_update.php
            # Intento 4: Usando los parámetros correctos según documentación encontrada
            # WELCOME_BOT_ENABLE: 'Y'
            # WELCOME_BOT_ID: bot_id
            # WELCOME_BOT_JOIN: 'always' (o 'first')
            
            payload = {
                "CONFIG_ID": line_id,
                "PARAMS": {
                    "WELCOME_BOT_ENABLE": "Y",
                    "WELCOME_BOT_ID": int(bot_id),
                    "WELCOME_BOT_JOIN": "always", # Para que se una siempre que sea posible
                    "WELCOME_BOT_TIME": 60,       # Tiempo antes de transferir si no resuelve
                    "WELCOME_BOT_LEFT": "queue"   # Que hacer si se va (queue = transferir a cola)
                }
            }
            
            # NOTA: La documentación oficial de imopenlines.config.update dice que toma 'PARAMS'. 
            # Si PARAMS falla, intentaremos pasar los campos directamente.
            
            result = auth.call_bitrix_method("imopenlines.config.update", payload)
            
            if "result" in result and result["result"]:
                print(f"✅ Línea {line_id} actualizada exitosamente.")
            else:
                print(f"⚠️ Posible error actualizando línea {line_id}:")
                print(result)

    except Exception as e:
        print(f"❌ Excepción fatal: {e}")

if __name__ == "__main__":
    # Permitir pasar IDs por argumentos si se desea
    lines_arg = [64, 66]
    if len(sys.argv) > 1:
        try:
            lines_arg = [int(x) for x in sys.argv[1:]]
        except ValueError:
            print("Argumentos inválidos. Usando por defecto [64, 66]")
            
    bind_bot_to_lines(lines_arg)
