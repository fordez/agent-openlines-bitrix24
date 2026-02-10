"""
Verification script for Deal Tools.
"""
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

from tools.deal.deal_list import deal_list
from tools.deal.deal_get import deal_get
from tools.deal.deal_update_info import deal_update_info
from tools.deal.deal_add_note import deal_add_note

def verify():
    print("🔍 1. Testing deal_list...")
    # List all open deals
    deals_output = deal_list(filter_params={"CLOSED": "N"}, select=["ID", "TITLE"])
    print(deals_output)
    
    if "Deals encontrados" not in deals_output:
        print("⚠️ No open deals found to test further. Please ensure there is at least one open deal.")
        return

    # Extract first deal ID from output (simple parsing for verification)
    try:
        # Assuming format "- ID: 123 | Title..."
        first_line = deals_output.split("\n")[1]
        deal_id = first_line.split("ID: ")[1].split(" |")[0].strip()
        print(f"👉 Using Deal ID for further tests: {deal_id}")
    except:
        print("❌ Could not extract deal ID from list output.")
        return

    print(f"\n🔍 2. Testing deal_get for ID {deal_id}...")
    deal_info = deal_get(deal_id)
    print(deal_info)
    
    if "Deal ID:" not in deal_info:
        print("❌ deal_get failed.")
        return

    print(f"\n🔍 3. Testing deal_add_note for ID {deal_id}...")
    note_result = deal_add_note(deal_id, "Verificación automática de herramientas de Deal.")
    print(note_result)

    print(f"\n🔍 4. Testing deal_update_info for ID {deal_id}...")
    # Update a harmless field like COMMENTS or a custom field if known. 
    # Using COMMENTS as it's standard.
    update_result = deal_update_info(deal_id, {"COMMENTS": "Updated by verification script."})
    print(update_result)
    
    print("\n✅ Verification sequence completed. Please check Bitrix24 to confirm changes.")
    print("⚠️ deal_move_stage and deal_mark_closed were NOT tested automatically to avoid disrupting real deals.")

if __name__ == "__main__":
    try:
        verify()
    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
