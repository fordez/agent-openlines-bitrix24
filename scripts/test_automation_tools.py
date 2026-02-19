"""
Script de prueba para las herramientas de Automatización CRM.
"""
from tools.automation.detect_sales_stage import detect_sales_stage
from tools.automation.predict_close_probability import predict_close_probability
from tools.automation.handle_objection import handle_objection
from tools.automation.reactivate_lead import reactivate_lead
from tools.deal.get_or_create_deal import get_or_create_deal
from tools.crm.resolve_identity import resolve_identity
from dotenv import load_dotenv

load_dotenv()

def test_automation_flow():
    print("--- Test Automation CRM Tools Flow ---")
    
    # Setup: Get Deal
    print(f"\n0. Setup: Getting deal for Test User Auto...")
    contact_id = resolve_identity(phone="5554443333", name="Test User Auto")
    deal_id = get_or_create_deal(contact_id, title="Deal Auto Test")
    print(f"Deal ID: {deal_id}")
    
    if not deal_id or "Error" in deal_id:
        print("❌ Failed to set up deal. Aborting.")
        return

    # 1. Detect Sales Stage
    print(f"\n1. Detecting sales stage from 'Cuanto cuesta el paquete?'...")
    detect_res = detect_sales_stage(deal_id, "Hola, me interesa saber cuanto cuesta el paquete premium")
    print(f"Result (Budget): {detect_res}")

    print(f"\n1.b Detecting sales stage from 'Lo quiero comprar ya'...")
    detect_res_2 = detect_sales_stage(deal_id, "Excelente, lo quiero comprar ya, aceptan tarjeta?")
    print(f"Result (Purchase): {detect_res_2}")

    # 2. Handle Objection
    print(f"\n2. Handling objection 'Es muy caro'...")
    obj_res = handle_objection(deal_id, "Es muy caro para mi presupuesto", "Ofrecimos pago en 3 cuotas")
    print(f"Result: {obj_res}")

    # 3. Predict Probability
    print(f"\n3. Predicting probability from analysis...")
    pred_res = predict_close_probability(deal_id, "Cliente muy interesado, urge comprar para la proxima semana")
    print(f"Result: {pred_res}")

    # 4. Reactivate Lead (Simulado con un ID arbitrario o el contacto si se comporta como lead)
    # Bitrix diferencia Leads de Contactos. Si no usamos Leads "viejos", esto fallará si le paso un Contact ID.
    # Intentaremos con un ID ficticio o conocido si no tenemos Leads en el flujo actual.
    # Para el test, probaremos, pero sabiendo que podría fallar si 'contact_id' no es un Lead ID.
    # print(f"\n4. Reactivating Lead/Contact {contact_id}...")
    # react_res = reactivate_lead(contact_id) # Probable error entity type incorrect
    # print(f"Result: {react_res}")

    print("\n--- End Test ---")

if __name__ == "__main__":
    test_automation_flow()
