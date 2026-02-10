"""
Módulo principal del agente AI.
Coordina la gestión de sesiones, la interacción con el LLM y la ejecución del observador.
"""
import asyncio
import traceback
from app.memory import add_message
from app.sessions import (
    get_chat_lock, get_session, set_session, 
    create_new_session, cleanup_expired_sessions, remove_session
)
from app.observer import run_observer_agent

async def get_response(user_message: str, chat_id: str) -> str:
    """
    Envía un mensaje al agente AI y retorna la respuesta.
    Reutiliza sesiones existentes para mantener contexto multi-turno nativo.
    Usa lock por chat_id: conversaciones diferentes NO se bloquean entre sí.
    """
    # Limpiar sesiones expiradas periódicamente (no bloquea otros chats)
    asyncio.create_task(_safe_cleanup())

    # Obtener lock específico para este chat
    chat_lock = await get_chat_lock(chat_id)

    async with chat_lock:
        # Buscar sesión existente
        session = get_session(chat_id)

        # Si no hay sesión o expiró, crear una nueva
        if session is None or session.is_expired():
            if session and session.is_expired():
                try:
                    await session.agent.__aexit__(None, None, None)
                except Exception:
                    pass
            session = await create_new_session(chat_id)
            await set_session(chat_id, session)

        session.touch()

        try:
            # 1. Guardar mensaje del usuario en memoria persistente
            await add_message(chat_id, "user", user_message)

            # 2. Enviar al LLM (contexto multi-turno nativo de mcp-agent)
            result = await session.llm.generate_str(message=user_message)

            # Fallback si retorna vacío
            ai_response = result or "Lo siento, no pude generar una respuesta."

            # 3. Guardar respuesta del bot en memoria persistente
            await add_message(chat_id, "assistant", ai_response)

            # 4. Lanzar Observador en Paralelo (Fire and forget)
            asyncio.create_task(run_observer_agent(chat_id, user_message, ai_response))

            return ai_response

        except Exception as e:
            print(f"❌ Error de mcp-agent: {e}")
            traceback.print_exc()

            # Invalidar sesión para recrear en próximo intento
            await remove_session(chat_id)
            try:
                await session.agent.__aexit__(None, None, None)
            except Exception:
                pass

            return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."

async def _safe_cleanup():
    """Wrapper seguro para limpieza de sesiones en background."""
    try:
        await cleanup_expired_sessions()
    except Exception:
        pass
