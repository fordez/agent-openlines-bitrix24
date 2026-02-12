import asyncio
import sys
import os

# Añadir el directorio raíz al path para importar tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.crm.lead_convert import lead_convert
from tools.crm.manage_lead import manage_lead

async def test_flexible_conversion():
    print("🚀 Iniciando prueba de conversión flexible...")

    # 1. Crear un Lead de prueba
    print("\n1. Creando Lead temporal...")
    lead_res = await manage_lead(
        name="Test Flexible",
        phone="+573001234567",
        title="Lead para Prueba Flexible"
    )
    
    if "ID:" not in lead_res:
        print(f"❌ Error creando lead: {lead_res}")
        return

    lead_id = int(lead_res.split("ID: ")[1].split(")")[0])
    print(f"✅ Lead creado ID: {lead_id}")

    # 2. Probar conversión SOLO CONTACTO (caso común para bases de datos)
    print(f"\n2. Probando conversión SOLO CONTACTO para Lead {lead_id}...")
    convert_res = await lead_convert(
        lead_id=lead_id,
        create_deal=False,
        create_contact=True,
        create_company=False
    )
    
    print(f"Resultado: {convert_res}")
    
    if "CONTACTO:" in convert_res and "DEAL:" not in convert_res:
        print("✅ Prueba Exitosa: Se creó Contacto pero NO Deal.")
    else:
        print("❌ Falló la prueba de solo contacto.")

if __name__ == "__main__":
    asyncio.run(test_flexible_conversion())
