import asyncio
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mocking session_crm_get to avoid needing a live chat_id for logic testing
async def mock_session_crm_get(chat_id):
    return 'CRM VINCULADO: {"CONTACT": "51922", "DEAL": "10382"}'

# Import strictly from the tool file
from tools.crm.crm_identity_update import crm_identity_update

async def test_logic():
    print("--- Probando Lógica de crm_identity_update (MOCK) ---")
    
    # Inyectamos el mock
    import tools.crm.crm_identity_update
    tools.crm.crm_identity_update.session_crm_get = mock_session_crm_get
    
    result = await crm_identity_update(
        chat_id=123, 
        name="Juan", 
        last_name="Prueba", 
        phone="+123456789"
    )
    print(f"Resultado: {result}")

if __name__ == "__main__":
    asyncio.run(test_logic())
