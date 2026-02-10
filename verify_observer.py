"""
Verification script for Parallel Observer Agent.
Simulate the async execution of the observer agent logic.
"""
import sys
import os
import asyncio
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.getcwd())
load_dotenv()

from app.agent import run_observer_agent

async def verify_observer():
    print("🚀 Iniciando prueba del Agente Observador...")
    
    # Simular una conversación interesante para activar el observador
    # Caso 1: Cliente satisfecho, agendó -> Nota
    chat_id = "test_observer_001"
    user_msg = "Listo, agendamos para mañana a las 10am. Gracias."
    ai_resp = "Perfecto, te he enviado la invitación. ¡Hasta mañana!"
    
    print("\n--- TEST 1: Nota de agendamiento ---")
    await run_observer_agent(chat_id, user_msg, ai_resp)
    
    # Caso 2: Cliente pide humano -> Tarea
    chat_id = "test_observer_002"
    user_msg = "Necesito hablar con un supervisor, esto no me sirve."
    ai_resp = "Entiendo. Un asesor humano revisará su caso."
    
    print("\n--- TEST 2: Demanda de humano (Tarea) ---")
    await run_observer_agent(chat_id, user_msg, ai_resp)
    
    print("\n✅ Prueba finalizada. Revisa los logs de arriba para ver 'Actividad registrada' o 'Tarea creada'.")

if __name__ == "__main__":
    asyncio.run(verify_observer())
