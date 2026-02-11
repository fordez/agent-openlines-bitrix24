import asyncio
import sys
import os
import random

# Añadir el directorio raíz al path para importar tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.crm.manage_lead import manage_lead

async def test_manage_lead():
    print("🚀 Iniciando verificación de manage_lead...")
    
    # Generar un número aleatorio para evitar conflictos con tests anteriores
    suffix = random.randint(1000, 9999)
    test_phone = f"+54911{suffix}"
    test_name = f"TestUser_{suffix}"
    
    # 1. Crear nuevo Lead (Escenario: No existe)
    print(f"\n--- Test 1: Crear Lead Nuevo ({test_phone}) ---")
    res_create = await manage_lead(
        name=test_name,
        phone=test_phone,
        title=f"Test Lead {suffix}"
    )
    print(f"Resultado 1: {res_create}")
    
    if "ID:" not in res_create:
        print("❌ Falló la creación del lead.")
        return

    # Extraer ID
    lead_id = res_create.split("ID: ")[1].split(")")[0]
    print(f"✅ Lead creado con ID: {lead_id}")

    print("⏳ Esperando 2s para indexación...")
    await asyncio.sleep(2)

    # 2. Actualizar Lead (Escenario: Ya existe)
    print(f"\n--- Test 2: Actualizar Lead Existente ---")
    res_update = await manage_lead(
        name=test_name,
        phone=test_phone, # Mismo teléfono -> Debe encontrar el lead anterior
        comments="Comentario agregado en Update"
    )
    print(f"Resultado 2: {res_update}")
    
    if "actualizado" in res_update and lead_id in res_update:
        print("✅ Correctamente identificado y actualizado.")
    else:
        print("❌ Falló la actualización (no detectó duplicado o no actualizó).")

    # 3. Datos parciales (Escenario: Solo email)
    print(f"\n--- Test 3: Crear Lead solo con Email ---")
    test_email = f"test_{suffix}@example.com"
    res_email = await manage_lead(
        email=test_email,
        name=f"Email Only User {suffix}"
    )
    print(f"Resultado 3: {res_email}")
    
    if "ID:" in res_email:
        print("✅ Lead por email creado correctamente.")
    else:
        print("❌ Falló creación por email.")

    print("\n🎉 Verificación completada.")

if __name__ == "__main__":
    asyncio.run(test_manage_lead())
