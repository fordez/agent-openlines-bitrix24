import os
import sys
from dotenv import load_dotenv

def verify():
    print("--- Verificación de Entorno ---")
    
    # Intentar cargar .env
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_file = os.path.join(base_dir, ".env")
    
    print(f"Buscando .env en: {env_file}")
    if os.path.exists(env_file):
        print("✅ Archivo .env encontrado.")
        load_dotenv(env_file)
    else:
        print("❌ Archivo .env NO encontrado.")
        
    vars_to_check = [
        "BITRIX_DOMAIN",
        "ACCESS_TOKEN",
        "REFRESH_TOKEN",
        "BOT_CODE",
        "WEBHOOK_HANDLER_URL"
    ]
    
    for var in vars_to_check:
        val = os.environ.get(var) or os.getenv(var)
        if val:
            # Mostrar primeros 5 caracteres por seguridad
            clean_val = str(val).strip("'\"")
            print(f"✅ {var}: {clean_val[:5]}... (Longitud: {len(clean_val)})")
        else:
            print(f"❌ {var}: NO DEFINIDA")

    print("--- Fin de Verificación ---")

if __name__ == "__main__":
    verify()
