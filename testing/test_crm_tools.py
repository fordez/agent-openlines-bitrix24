"""
Script de prueba para las herramientas CRM.
"""
from tools.crm.resolve_identity import resolve_identity
from tools.crm.enrich_identity import enrich_identity
from tools.crm.qualify_lead import qualify_lead
import os
from dotenv import load_dotenv

load_dotenv()

def test_crm_flow():
    print("--- Test CRM Flow ---")
    
    # 1. Resolve Identity
    # Usamos un número falso para probar la creación o búsqueda
    phone = "5551234567"
    email = "test_crm_tool@example.com"
    name = "Test User CRM"
    
    print(f"\n1. Resolving identity for {name} ({phone}, {email})...")
    entity_id = resolve_identity(phone=phone, email=email, name=name)
    print(f"Result: {entity_id}")
    
    if not entity_id or "Error" in entity_id:
        print("❌ Failed to resolve identity. Aborting.")
        return

    # 2. Enrich Identity
    print(f"\n2. Enriching identity for {entity_id}...")
    enrich_result = enrich_identity(entity_id, {
        "COMMENTS": "Cliente de prueba creado por script de verificación.",
        "SOURCE_DESCRIPTION": "Test Script"
    })
    print(f"Result: {enrich_result}")

    # 3. Qualify Lead
    print(f"\n3. Qualifying lead {entity_id}...")
    qualify_result = qualify_lead(
        entity_id=entity_id,
        intention="Prueba de sistema",
        score=50,
        next_action="Verificar logs"
    )
    print(f"Result: {qualify_result}")
    
    print("\n--- End Test ---")

if __name__ == "__main__":
    test_crm_flow()
