import json
from dotenv import load_dotenv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import auth
import asyncio

async def check_bindings():
    print("Obteniendo lista de eventos vinculados (event.get)...")
    
    try:
        result = await auth.call_bitrix_method("event.get")
        
        if "result" in result:
            events = result["result"]
            print(f"Se encontraron {len(events)} eventos vinculados:")
            print(json.dumps(events, indent=2))
        else:
            print("No se encontraron eventos o respuesta inesperada.")
            print(result)

    except Exception as e:
        print(f"Error al obtener eventos: {e}")

if __name__ == "__main__":
    asyncio.run(check_bindings())
