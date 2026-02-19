"""
Script de prueba para las herramientas de Calendario.
"""
from tools.calendar.get_availability import get_availability
from tools.calendar.create_event import create_event
from tools.calendar.update_event import update_event
from tools.calendar.reschedule_event import reschedule_event
from tools.calendar.cancel_event import cancel_event
from tools.calendar.get_event import get_event
from tools.calendar.schedule_meeting import schedule_meeting
from tools.crm.resolve_identity import resolve_identity
from datetime import datetime, timedelta
import json
from dotenv import load_dotenv

load_dotenv()

def test_calendar_flow():
    print("--- Test Calendar Tools Flow ---")
    
    # Fechas de prueba (mañana)
    tomorrow = datetime.now() + timedelta(days=1)
    from_date = tomorrow.strftime("%Y-%m-%d")
    to_date = tomorrow.strftime("%Y-%m-%d")
    
    start_time = f"{from_date} 10:00:00"
    end_time = f"{to_date} 11:00:00"

    # 1. Get Availability
    print(f"\n1. Checking availability for {from_date}...")
    avail = get_availability(from_date, to_date)
    print(f"Availability result: {avail[:100]}...") # Truncated

    # 2. Create Event
    print(f"\n2. Creating event 'Test Event AI'...")
    event_result = create_event("Test Event AI", start_time, end_time, "Created by test script")
    print(f"Result: {event_result}")
    
    if "Error" in event_result:
        print("❌ Failed to create event. Aborting.")
        return
        
    # Extract ID (simple parsing, assuming format "Evento creado exitosamente: ID")
    try:
        event_id = event_result.split(": ")[1]
    except:
        print(f"❌ Could not parse event ID from: {event_result}")
        return

    # 3. Get Event
    print(f"\n3. Getting details for event {event_id}...")
    details = get_event(event_id)
    print(f"Details length: {len(details)}")

    # 4. Update Event
    print(f"\n4. Updating event {event_id}...")
    update_result = update_event(event_id, {"name": "Test Event AI (Updated)", "description": "Updated by script"})
    print(f"Result: {update_result}")

    # 4.5 Reschedule Event
    print(f"\n4.5 Rescheduling event {event_id}...")
    # Move forward 2 hours
    new_start = (tomorrow + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
    new_end = (tomorrow + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")
    reschedule_result = reschedule_event(event_id, new_start, new_end)
    print(f"Result: {reschedule_result}")

    # 5. Schedule Meeting (CRM Integration)
    print(f"\n5. Scheduling CRM meeting...")
    # Need a contact first
    contact_id = resolve_identity(phone="5559998888", name="Test Calendar User")
    if contact_id and "Error" not in contact_id:
        meeting_result = schedule_meeting(
            contact_id, 
            "Reunión de Ventas AI", 
            f"{from_date} 14:00:00", 
            f"{to_date} 15:00:00", 
            "Discusión de propuesta"
        )
        print(f"Meeting Result: {meeting_result}")
    else:
        print("⚠️ Skipping schedule_meeting test (no contact resolved)")

    # 6. Cancel Event (Cleanup)
    print(f"\n6. Cancelling event {event_id}...")
    cancel_result = cancel_event(event_id)
    print(f"Result: {cancel_result}")

    print("\n--- End Test ---")

if __name__ == "__main__":
    test_calendar_flow()
