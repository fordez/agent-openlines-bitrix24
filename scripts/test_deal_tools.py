"""
Script de prueba para las herramientas CRM de Deals.
"""
from tools.crm.resolve_identity import resolve_identity
from tools.deal.get_or_create_deal import get_or_create_deal
from tools.deal.update_deal_stage import update_deal_stage
from tools.deal.update_deal_fields import update_deal_fields
from tools.deal.add_deal_note import add_deal_note
from tools.deal.close_deal import close_deal
from dotenv import load_dotenv

load_dotenv()

def test_deal_flow():
    print("--- Test Deal CRM Flow ---")
    
    # 1. Resolve Identity (necesitamos un contacto para el deal)
    phone = "5559876543"
    name = "Test User Deal"
    print(f"\n1. Resolving identity for {name}...")
    contact_id = resolve_identity(phone=phone, name=name)
    print(f"Contact ID: {contact_id}")
    
    if not contact_id or "Error" in contact_id:
        print("❌ Failed to resolve identity. Aborting.")
        return

    # 2. Get or Create Deal
    print(f"\n2. Get or Create Deal for contact {contact_id}...")
    deal_id = get_or_create_deal(contact_id, title=f"Deal Test {name}")
    print(f"Deal ID: {deal_id}")

    if not deal_id or "Error" in deal_id:
        print("❌ Failed to get/create deal. Aborting.")
        return

    # 3. Update Deal Fields
    print(f"\n3. Updating deal fields...")
    update_result = update_deal_fields(deal_id, {
        "OPPORTUNITY": 1500,
        "CURRENCY_ID": "USD",
        "COMMENTS": "Presupuesto inicial asignado por test script."
    })
    print(f"Result: {update_result}")

    # 4. Add Node
    print(f"\n4. Adding note to deal...")
    note_result = add_deal_note(deal_id, "El cliente está interesado en paquete premium.")
    print(f"Result: {note_result}")

    # 5. Update Stage (opcional, depende de configuración de bitrix)
    # print(f"\n5. Updating stage to PREPARATION...")
    # stage_result = update_deal_stage(deal_id, "PREPARATION")
    # print(f"Result: {stage_result}")

    # 6. Close Deal (Won)
    print(f"\n6. Closing deal as WON...")
    close_result = close_deal(deal_id, won=True, close_comment="Cierre exitoso por test script.")
    print(f"Result: {close_result}")

    print("\n--- End Test ---")

if __name__ == "__main__":
    test_deal_flow()
