"""
Módulo principal del agente AI.
Coordina la gestión de sesiones, la interacción con el LLM.
"""
import asyncio
import traceback
import sys

# Redirect all prints to stderr to avoid breaking MCP protocol
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)

from app.memory import add_message
from app.sessions import (
    get_chat_lock, get_session, set_session, 
    create_new_session, cleanup_expired_sessions, remove_session
)
from app.bitrix import send_typing_indicator
from app.metrics import MetricsService

async def get_response(user_message: str, chat_id: str, event_token: str = None, client_endpoint: str = None, session_id: int = None, user_name: str = None, user_id: str = None, chat_id_num: int = None) -> str:
    """
    Envía un mensaje al agente AI y retorna la respuesta.
    Recibe chat_id (dialog_id) y opcionalmente chat_id_num (el ID numérico para tools).
    """
    # Typing indicator usa token del EVENTO (para que Bitrix sepa quién escribe)
    if event_token and client_endpoint:
        asyncio.create_task(send_typing_indicator(event_token, client_endpoint, chat_id, "on"))

    # Obtener lock específico para este chat
    chat_lock = await get_chat_lock(chat_id)

    try:
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
                # Incluimos info de contexto para el Agente AI (Usamos nombres inequívocos)
                context_list = []
                if session_id: context_list.append(f"BITRIX_SESSION_ID={session_id}")
                if chat_id_num: context_list.append(f"BITRIX_CHAT_ID={chat_id_num}")
                if user_name: context_list.append(f"USER_NAME={user_name}")
                if user_id: context_list.append(f"USER_ID={user_id}")
                if client_endpoint: context_list.append(f"client_endpoint={client_endpoint}")
                context_list.append(f"DIALOG_ID={chat_id}")
                
                from datetime import datetime
                now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                context_prefix = (
                    f"[FECHA Y HORA ACTUAL: {now_str}]\n"
                    f"[CONTEXTO ACTUAL: {', '.join(context_list)}]\n\n"
                    "⚠️ NOTA: El `BITRIX_CHAT_ID` numérico es el que debes usar para herramientas del CRM.\n"
                    "⚠️ NOTA: IMPORTANTE - Al llamar a `manage_lead`, DEBES incluir el Nombre y el Teléfono/Email recolectados como argumentos explicitamente.\n"
                    "⚠️ NOTA: NO necesitas pasar `access_token` a las herramientas.\n"
                )
                
                full_message = f"{context_prefix}{user_message}"
                await add_message(chat_id, "user", full_message)

                # 2. Enviar al LLM (contexto multi-turno nativo de mcp-agent)
                print(f"  📤 Enviando a LLM: {user_message[:50]}...")
                response = await session.llm.generate(message=full_message)
                print(f"  📥 Respuesta raw LLM type: {type(response)}")

                # Extraer texto de la respuesta de forma segura
                ai_response = ""
                try:
                    # Debug deep inspection
                    if isinstance(response, list):
                        for i, content in enumerate(response):
                            print(f"    Item {i}: type={type(content)}")
                            if hasattr(content, 'parts'):
                                print(f"      Parts: {content.parts}")
                            if hasattr(content, 'role'):
                                print(f"      Role: {content.role}")
                            if hasattr(content, 'content'):
                                print(f"      Content: {content.content}")

                    # Standard extraction
                    for content in response:
                        # Case 1: Google/Vertex style (has parts)
                        if hasattr(content, 'parts') and content.parts:
                            for part in content.parts:
                                if hasattr(part, 'text') and part.text:
                                    ai_response += part.text
                                elif isinstance(part, str):
                                    ai_response += part
                        
                        # Case 2: OpenAI style (ChatCompletionMessage with .content)
                        elif hasattr(content, 'content') and content.content:
                            ai_response += content.content
                        
                        
                        # Case 4: Tool call result (no content)
                        elif hasattr(content, 'content') and content.content is None:
                            pass

                        else:
                            print(f"      ⚠️ Unknown content type: {type(content)}")

                    if not ai_response and hasattr(response, 'text'):
                         # Fallback for some LLM wrappers
                         ai_response = response.text

                except Exception as e:
                    print(f"  ❌ Error parsing response: {e}")
                    traceback.print_exc()

                print(f"  💡 AI Response final: '{ai_response}'")

                # 3. Guardar respuesta del bot en memoria persistente
                if ai_response:
                    await add_message(chat_id, "assistant", ai_response)
                else:
                     print("  ⚠️ AI Response is empty!")
                     ai_response = "Lo siento, no pude generar una respuesta en este momento."

                # Desactivar typing indicator
                if event_token and client_endpoint:
                    asyncio.create_task(send_typing_indicator(event_token, client_endpoint, chat_id, "off"))

                # 4. Registrar métricas de tokens (Async)
                try:
                    # Intento genérico de extraer usage, depende del provider
                    prompt_tokens = 0
                    completion_tokens = 0
                    
                    # OpenAI style
                    if hasattr(response, 'usage') and response.usage:
                        prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                        completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                    
                    if prompt_tokens > 0:
                        metrics = await MetricsService.get_instance()
                        # Extraer tenant_id
                        from app.context_vars import member_id_var
                        current_tenant = member_id_var.get() or "unknown"
                        
                        # Asumimos que session.llm tiene el modelo configurado
                        model_name = "unknown"
                        if hasattr(session, 'llm') and hasattr(session.llm, 'model'):
                            model_name = session.llm.model

                        await metrics.log_token_usage(current_tenant, prompt_tokens, completion_tokens, model_name)
                        print(f"📊 [Metrics] Tokens logged: {prompt_tokens} + {completion_tokens}")

                except Exception as e:
                    print(f"⚠️ Error logging metrics: {e}")

                return ai_response

            except Exception as e:
                print(f"❌ Error de mcp-agent en get_response: {e}")
                traceback.print_exc()

                # Invalidar sesión para recrear en próximo intento
                await remove_session(chat_id)
                
                # Limpieza segura si la sesión llegó a existir
                if 'session' in locals() and session:
                    try:
                        if hasattr(session.agent, '__aexit__'):
                            await session.agent.__aexit__(None, None, None)
                        if session.app_context_manager and hasattr(session.app_context_manager, '__aexit__'):
                            await session.app_context_manager.__aexit__(None, None, None)
                    except Exception as cleanup_err:
                        print(f"  ⚠️ Error en limpieza post-error: {cleanup_err}")

                return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."

    except Exception as lock_err:
        # Check specific LockError logic if needed
        if "lock" in str(lock_err).lower():
            print(f"⏳ [Agent] Timeout esperando lock para {chat_id}: {lock_err}")
            return "Lo siento, el sistema está recibiendo muchas peticiones. Por favor intenta de nuevo en unos segundos."
        
        # Re-raise other errors or return generic
        print(f"💥 Error crítico fuera del lock: {lock_err}")
        return "Error del sistema."


async def _safe_cleanup():
    """Wrapper seguro para limpieza de sesiones en background."""
    try:
        await cleanup_expired_sessions()
    except Exception:
        pass
