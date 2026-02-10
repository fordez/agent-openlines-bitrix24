"""
Script de prueba para las herramientas de Actividades CRM.
"""
from tools.activity.create_activity import create_activity
from tools.activity.update_activity import update_activity
from tools.activity.complete_activity import complete_activity
from tools.activity.schedule_followup import schedule_followup
from tools.crm.resolve_identity import resolve_identity
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_activity_flow():
    print("--- Test Activity CRM Tools Flow ---")
    
    # 1. Necesitamos un contacto
    print(f"\n1. Resolving identity for Test User Activity...")
    contact_id = resolve_identity(phone="5551112222", name="Test User Activity")
    print(f"Contact ID: {contact_id}")
    
    if not contact_id or "Error" in contact_id:
        print("❌ Failed to resolve identity. Aborting.")
        return

    # 2. Create Activity (Task)
    print(f"\n2. Creating Task activity...")
    task_res = create_activity(
        owner_type_id=3, # Contact
        owner_id=contact_id,
        description="Tarea de prueba creada por script AI",
        type_id=3, # Task
        subject="Tarea AI Test"
    )
    print(f"Result: {task_res}")

    # Parse ID
    try:
        activity_id = task_res.split(": ")[1]
    except:
        print("❌ Could not parse activity ID.")
        return

    # 3. Update Activity
    print(f"\n3. Updating activity {activity_id}...")
    update_res = update_activity(activity_id, {
        "DESCRIPTION": "Descripción actualizada por script.",
        "PRIORITY": 3 # High
    })
    print(f"Result: {update_res}")

    # 4. Complete Activity
    print(f"\n4. Completing activity {activity_id}...")
    complete_res = complete_activity(activity_id)
    print(f"Result: {complete_res}")

    # 5. Schedule Follow-up
    print(f"\n5. Scheduling follow-up call...")
    followup_res = schedule_followup(contact_id, "Llamada de seguimiento post-test", delay_days=2)
    print(f"Result: {followup_res}")

    print("\n--- End Test ---")

if __name__ == "__main__":
    test_activity_flow()
