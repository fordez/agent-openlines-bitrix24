from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_google import GoogleAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
import os
from app.context import app, MCP_SERVER_NAME
from app.prompts import OBSERVER_SYSTEM_PROMPT

async def run_observer_agent(chat_id: str, user_message: str, ai_response: str):
    """
    Ejecuta el Agente Observador en paralelo para registrar actividades/tareas.
    """
    print(f"  👀 [Observer] Iniciando análisis para chat {chat_id}...")
    try:
        context = (
            f"CHAT_ID: {chat_id}\n"
            f"USER MESSAGE: {user_message}\n"
            f"AGENT RESPONSE: {ai_response}\n\n"
            "Analiza esta interacción y decide si registrar Activity o Task."
        )

        async with app.run() as agent_app:
            observer = Agent(
                name=f"observer_{chat_id}",
                instruction=OBSERVER_SYSTEM_PROMPT,
                server_names=[MCP_SERVER_NAME],
            )

            async with observer:
                llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
                if llm_provider == "openai":
                    llm = await observer.attach_llm(OpenAIAugmentedLLM)
                else:
                    llm = await observer.attach_llm(GoogleAugmentedLLM)

                result = await llm.generate_str(message=context)
                print(f"  👀 [Observer] Resultado: {result}")

    except Exception as e:
        print(f"  ❌ [Observer] Error: {e}")
