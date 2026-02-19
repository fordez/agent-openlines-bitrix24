import asyncio
import sys
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.crm.enrich_identity import enrich_identity

async def manual_test():
    print("🧪 PROBANDO HERRAMIENTA 'enrich_identity' MANUALMENTE")
    print("-" * 50)
    
    # Simular los argumentos que recibe la tool ahora (sin tokens)
    name = "Jaime"
    phone = "3143964611"
    
    print(f"📡 Llamando a enrich_identity(name='{name}', phone='{phone}')")
    
    try:
        # Esto debería usar el TokenManager internamente
        result = await enrich_identity(name=name, phone=phone)
        print("\n✅ RESULTADO OBTENIDO:")
        print(result)
    except Exception as e:
        print("\n❌ ERROR DURANTE LA PRUEBA:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Importante: cargar env vars por si acaso no están cargadas
    from dotenv import load_dotenv
    load_dotenv()
    
    print(f"🌍 REDIS_URL en el script: {os.getenv('REDIS_URL')}")
    
    asyncio.run(manual_test())
