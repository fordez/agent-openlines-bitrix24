"""
Verification script for Calendar Tools (New Implementation).
"""
import sys
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

from tools.calendar.calendar_get_types import calendar_get_types
from tools.calendar.calendar_event_list import calendar_event_list
from tools.calendar.calendar_availability_check import calendar_availability_check
from tools.calendar.calendar_event_create import calendar_event_create
from tools.calendar.calendar_event_update import calendar_event_update
from tools.calendar.calendar_event_delete import calendar_event_delete
from tools.calendar.calendar_event_set_reminder import calendar_event_set_reminder

def verify():
    print("🗓️ 1. Tipos de Calendario:")
    print(calendar_get_types())

    print("\n🗓️ 2. Agenda actual (próximos 3 días):")
    print(calendar_event_list(to_date=(datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')))

    print("\n🗓️ 3. Creando evento de prueba...")
    # Crear para mañana a las 10am
    tomorrow = datetime.now() + timedelta(days=1)
    from_ts = tomorrow.replace(hour=10, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
    
    event_result = calendar_event_create(
        name="[TEST] Verificación Agente",
        from_ts=from_ts,
        duration_mins=30,
        description="Evento temporal de prueba auto-creado."
    )
    print(event_result)
    
    if "ID: " not in event_result:
        print("❌ Falló creación de evento.")
        return

    event_id = event_result.split("ID: ")[1].strip()
    print(f"👉 ID del evento creado: {event_id}")

    print("\n🗓️ 4. Verificando disponibilidad (debería salir ocupado ese hueco)...")
    # Nota: Availability check necesita user ID, usaremos lista vacía o intentaremos con el current user si la función lo maneja
    # En nuestra impl, availability_check pide 'users'. Si no tenemos ID, usaremos '1' (admin/bot usually) o fallará.
    # Asumimos user 1 para test.
    print(calendar_availability_check(
        from_date=tomorrow.strftime('%Y-%m-%d'),
        to_date=tomorrow.strftime('%Y-%m-%d'),
        users=[1] 
    ))

    print("\n🗓️ 5. Reagendando evento (mover 1 hora después)...")
    moved_ts = (datetime.strptime(from_ts, '%Y-%m-%d %H:%M:%S') + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    print(calendar_event_update(event_id, from_ts=moved_ts, duration_mins=30))

    print("\n🗓️ 6. Configurando recordatorio (15 min antes)...")
    print(calendar_event_set_reminder(event_id, 15))

    print("\n🗓️ 7. Eliminando evento de prueba...")
    print(calendar_event_delete(event_id))
    
    print("\n✅ Verificación de calendario finalizada.")

if __name__ == "__main__":
    verify()
