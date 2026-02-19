import asyncio
import sys
import os

# Añadir el path raíz para importar módulos de la app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.calendar.calendar_event_create import calendar_event_create
from tools.task.task_create import task_create

async def test_failures():
    print("🚀 Probando calendar_event_create...")
    res_cal = await calendar_event_create(
        title="Test Event Repro",
        start_time="2026-03-01 10:00:00",
        end_time="2026-03-01 11:00:00",
        description="Repro error ownerId"
    )
    print(f"RESULTADO CALENDARIO: {res_cal}\n")

    print("🚀 Probando task_create...")
    res_task = await task_create(
        title="Test Task Repro",
        description="Repro error responsible",
        responsible_id=None
    )
    print(f"RESULTADO TAREA: {res_task}\n")

if __name__ == "__main__":
    asyncio.run(test_failures())
