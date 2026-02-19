import asyncio
import sys
import os

# Asegurar que el path incluya la raíz del proyecto para importar app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import auth

async def check_contact(contact_id: int):
    print(f"--- Investigando Contacto {contact_id} ---")
    
    # 1. Obtener datos del contacto
    result = await auth.call_bitrix_method("crm.contact.get", {"id": contact_id})
    print(f"Datos del contacto: {result.get('result')}")
    
    # 2. Buscar deals relacionados
    deals = await auth.call_bitrix_method("crm.deal.list", {
        "filter": {"CONTACT_ID": contact_id},
        "select": ["ID", "TITLE", "STAGE_ID", "DATE_CREATE"]
    })
    print(f"Deals relacionados: {deals.get('result')}")
    
    # 3. Buscar leads relacionados
    leads = await auth.call_bitrix_method("crm.lead.list", {
        "filter": {"CONTACT_ID": contact_id},
        "select": ["ID", "TITLE", "STATUS_ID", "DATE_CREATE"]
    })
    print(f"Leads relacionados: {leads.get('result')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cid = int(sys.argv[1])
    else:
        cid = 51922
    asyncio.run(check_contact(cid))
