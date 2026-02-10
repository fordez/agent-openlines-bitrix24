import json
from dotenv import load_dotenv
import auth

# Cargar variables de entorno
load_dotenv()

def check_bindings():
    print("Obteniendo lista de eventos vinculados (event.get)...")
    
    try:
        result = auth.call_bitrix_method("event.get")
        
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
    check_bindings()
