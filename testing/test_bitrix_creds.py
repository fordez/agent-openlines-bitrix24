import asyncio
import sys
import os
from datetime import datetime

# Añadir el path raíz para importar módulos de la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.token_manager import get_token_manager
from app.auth import call_bitrix_method

async def run_diagnostic():
    print("🔍 INICIANDO DIAGNÓSTICO DE CREDENCIALES BITRIX24\n")
    print(f"⏰ Hora: {datetime.now().isoformat()}")
    print(f"🌐 Dominio: {os.getenv('BITRIX_DOMAIN')}")
    print("-" * 50)

    try:
        # 1. Obtener TokenManager
        print("1. Cargando TokenManager...")
        tm = await get_token_manager()
        token = await tm.get_token()
        
        if not token:
            print("❌ ERROR: No se pudo obtener el token de Redis/TokenManager")
            return

        print(f"✅ Token obtenido (primeros 15 caracteres): {token[:15]}...")

        # 2. Probar llamadas a la API
        methods_to_test = [
            ("user.current", {}, "Permisos Básicos (App/User)"),
            ("crm.lead.list", {"select": ["ID", "TITLE"], "limit": 1}, "Permisos CRM Leads"),
            ("crm.contact.list", {"select": ["ID", "NAME"], "limit": 1}, "Permisos CRM Contactos"),
            ("imopenlines.config.list", {}, "Permisos OpenLines")
        ]

        for method, params, description in methods_to_test:
            print(f"\n📡 Probando: {method} ({description})...")
            try:
                response = await call_bitrix_method(method, params)
                if response:
                    print(f"   ✅ ÉXITO: Recibidos {len(str(response))} bytes de datos.")
                    # Si es lead list o contact list, mostrar si encontró algo
                    if "result" in response:
                        count = len(response["result"]) if isinstance(response["result"], list) else 1
                        print(f"   📊 Resultado: {count} registros encontrados.")
                else:
                    print(f"   ❌ ERROR: Respuesta vacía de {method}")
            except Exception as e:
                print(f"   ❌ ERROR en {method}: {str(e)}")

    except Exception as e:
        print(f"\n💥 ERROR FATAL EN EL DIAGNÓSTICO: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "-" * 50)
    print("🏁 DIAGNÓSTICO FINALIZADO")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
