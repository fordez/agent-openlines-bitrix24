import asyncio
import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.getcwd())

from tools.task.task_create import task_create

async def verify_task():
    print("Probando creación de tarea con lógica de usuario dinámica...")
    try:
        # No pasamos responsible_id para que lo obtenga dinámicamente
        res = await task_create(
            title="[TEST] Verificación ID Dinámico",
            description="Esta tarea verifica que el bot use un ID de responsable válido.",
            deadline_hours=1
        )
        print(f"✅ Resultado: {res}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(verify_task())
