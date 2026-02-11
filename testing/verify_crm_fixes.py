import asyncio
import sys
import os

# Añadir el directorio raíz al path para importar tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.crm.lead_add import lead_add
from tools.crm.lead_update import lead_update
from tools.openlines.session_crm_bind import session_crm_bind

async def test_crm_fixes():
    print("🚀 Iniciando verificación de fixes CRM...")
    
    # 1. Probar lead_add con datos completos
    # Usamos un chat_id ficticio para probar la lógica de vínculo
    print("\n--- Test 1: lead_add con vinculación ---")
    res_add = await lead_add(
        title="Test Lead Verificación",
        name="Juan",
        last_name="Prueba",
        phone="+5491100000000",
        chat_id=999999  # ID ficticio
    )
    print(f"Resultado lead_add: {res_add}")
    
    if "ID:" not in res_add:
        print("❌ Falló la creación del lead.")
        return

    lead_id = int(res_add.split("ID: ")[1].split(")")[0])
    print(f"✅ Lead creado con ID: {lead_id}")

    # 2. Probar lead_update
    print("\n--- Test 2: lead_update (actualizando teléfono) ---")
    res_update = await lead_update(
        lead_id=lead_id,
        phone="+5491199999999",
        comments="Actualizado durante verificación de fixes."
    )
    print(f"Resultado lead_update: {res_update}")
    
    if "exitosamente" in res_update:
        print("✅ lead_update funcionó correctamente.")
    else:
        print("❌ Falló lead_update.")

    # 3. Probar session_crm_bind manual
    print("\n--- Test 3: session_crm_bind manual ---")
    res_bind = await session_crm_bind(
        chat_id=999999,
        entity_id=lead_id,
        entity_type="LEAD"
    )
    print(f"Resultado session_crm_bind: {res_bind}")
    
    if "vinculado" in res_bind:
        print("✅ session_crm_bind funcionó correctamente.")
    else:
        print("❌ Falló session_crm_bind.")

    print("\n🎉 Verificación completada.")

if __name__ == "__main__":
    asyncio.run(test_crm_fixes())
