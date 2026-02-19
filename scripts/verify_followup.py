"""
Verification script for Followup Tools.
"""
import sys
import os
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

from tools.followup.lead_reactivate_by_client import lead_reactivate_by_client
from tools.followup.deal_detect_stage_for_client import deal_detect_stage_for_client
from tools.followup.deal_add_client_objection import deal_add_client_objection
from tools.followup.deal_update_probability_client import deal_update_probability_client
from tools.followup.lead_next_action_client import lead_next_action_client
from tools.followup.deal_next_action_client import deal_next_action_client
from tools.followup.deal_follow_up_schedule_client import deal_follow_up_schedule_client
from tools.followup.lead_follow_up_note_client import lead_follow_up_note_client
from tools.deal.deal_list import deal_list

def verify():
    # 1. Find a Deal for testing
    print("🔍 1. Buscando Deal activo...")
    deals_out = deal_list({}, ["ID", "TITLE", "STAGE_ID"])
    deal_id = None
    if "ID: " in deals_out:
        try:
             # Parse first deal
             deal_id = int(deals_out.split("ID: ")[1].split(" |")[0])
             print(f"👉 Usaremos Deal ID: {deal_id}")
        except:
             pass

    if deal_id:
        print(f"\n📊 2. Detectando etapa del Deal {deal_id}...")
        print(deal_detect_stage_for_client(deal_id))
        
        print(f"\n📝 3. Registrando objeción 'Está muy caro'...")
        print(deal_add_client_objection(deal_id, "El cliente dice que está muy caro."))
        
        print(f"\n📈 4. Actualizando probabilidad a 80%...")
        print(deal_update_probability_client(deal_id, 80))
        
        print(f"\n📅 5. Agendando próxima acción 'Enviar nueva cotización'...")
        print(deal_next_action_client(deal_id, "Enviar nueva cotización", 60))
        
        print(f"\n⏰ 6. Agendando seguimiento automático para mañana...")
        print(deal_follow_up_schedule_client(deal_id, "Preguntar si le gusto el precio", 24))

    # 7. Lead tests
    print(f"\n🔍 7. Buscando Lead para pruebas...")
    lead_id = 90
    try:
         # Try direct list using authenticated call if tool import fails or just use tool
         from tools.lead.lead_list import lead_list
         leads_res = lead_list() # Get default page
         if "ID: " in leads_res:
             lead_id = int(leads_res.split("ID: ")[1].split(" |")[0])
             print(f"👉 Usaremos Lead ID: {lead_id}")
    except Exception as e:
         print(f"⚠️ Error buscando lead: {e}")
         
    print(f"\n🔄 8. Reactivando Lead {lead_id} (Test)...")
    print(lead_reactivate_by_client(lead_id))
    
    print(f"\n📌 8. Agregando nota al Lead {lead_id}...")
    print(lead_follow_up_note_client(lead_id, "Cliente contactó por WhatsApp nuevamente."))
    
    print(f"\n📅 9. Agendando acción Lead 'Llamar urgente'...")
    print(lead_next_action_client(lead_id, "Llamar urgente", 30))

    print("\n✅ Verificación de Followup finalizada.")

if __name__ == "__main__":
    verify()
