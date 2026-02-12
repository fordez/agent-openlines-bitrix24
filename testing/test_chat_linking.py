import asyncio
import sys
import os

# Añadir el directorio raíz al path para importar tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.crm.manage_lead import manage_lead

async def test_linking():
    print("🚀 Iniciando verificación de vinculación Lead-Chat...")
    
    # Usamos el CHAT_ID 5112 que sabemos que existe y tiene metadata
    chat_id = 5112
    
    print(f"\n--- Probando manage_lead con CHAT_ID {chat_id} ---")
    result = await manage_lead(
        name="Test Vinculo",
        phone="+573000000000",
        email="test_vinculo@example.com",
        title="Lead Prueba Vinculo Chat",
        chat_id=chat_id
    )
    
    print(f"Resultado: {result}")
    
    if "ID:" in result:
        lead_id = result.split("ID: ")[1].split(")")[0]
        print(f"✅ Lead creado/actualizado con ID: {lead_id}")
        print(f"Sugerencia: Revisa en Bitrix24 el Lead {lead_id} para ver si aparece el botón de chat.")
    else:
        print("❌ Error en la gestión del Lead.")

if __name__ == "__main__":
    asyncio.run(test_linking())
