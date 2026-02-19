"""
Módulo principal del agente AI.
Coordina la gestión de sesiones, la interacción con el LLM.
"""
import asyncio
import traceback
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

            # Desactivar typing indicator
            if event_token and client_endpoint:
                asyncio.create_task(send_typing_indicator(event_token, client_endpoint, chat_id, "off"))

            return ai_response

        except Exception as e:
            print(f"❌ Error de mcp-agent: {e}")
            traceback.print_exc()

            # Invalidar sesión para recrear en próximo intento
            await remove_session(chat_id)
            try:
                await session.agent.__aexit__(None, None, None)
                if session.app_context_manager:
                    await session.app_context_manager.__aexit__(None, None, None)
            except Exception:
                pass

            # 4. Registrar métricas de tokens (Async)
            try:
                # Intento genérico de extraer usage, depende del provider
                prompt_tokens = 0
                completion_tokens = 0
                
                # OpenAI style
                if hasattr(response, 'usage') and response.usage:
                    prompt_tokens = getattr(response.usage, 'prompt_tokens', 0)
                    completion_tokens = getattr(response.usage, 'completion_tokens', 0)
                # Google style (candidate.usage_metadata?) - simplificado
                # Si no está disponible fácil, lo dejamos en 0 por ahora o implementamos lógica específica
                
                metrics = await MetricsService.get_instance()
                # Extraer tenant_id del chat_id o context si es posible
                # Por ahora usamos 'default' o el member_id si lo tenemos en contexto
                from app.context_vars import member_id_var
                current_tenant = member_id_var.get() or "unknown"
                
                # Asumimos que session.llm tiene el modelo configurado
                model_name = "unknown"
                if hasattr(session, 'llm') and hasattr(session.llm, 'model'):
                    model_name = session.llm.model

                if prompt_tokens > 0:
                    await metrics.log_token_usage(current_tenant, prompt_tokens, completion_tokens, model_name)
                    print(f"📊 [Metrics] Tokens logged: {prompt_tokens} + {completion_tokens}")

            except Exception as e:
                print(f"⚠️ Error logging metrics: {e}")

            return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor intenta de nuevo."

async def _safe_cleanup():
    """Wrapper seguro para limpieza de sesiones en background."""
    try:
        await cleanup_expired_sessions()
    except Exception:
        pass
