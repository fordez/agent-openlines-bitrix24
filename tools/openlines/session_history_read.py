"""
Tool to silently read the chat history of an Open Line session.
Uses imopenlines.session.history.get to read without being a visible participant.
"""
from app.auth import call_bitrix_method
import sys

async def session_history_read(session_id: int) -> str:
    """
    Lee el historial completo de una sesión de Open Lines de forma SILENCIOSA.
    El bot NO aparece como participante visible. Ideal para analizar la conversación
    entre un operador humano y el cliente, y generar notas internas con sugerencias.
    
    Args:
        session_id: ID de la sesión de Open Lines a leer.
    """
    sys.stderr.write(f"  🔍 Tool session_history_read: session_id={session_id}\n")
    
    try:
        result = await call_bitrix_method("imopenlines.session.history.get", {
            "SESSION_ID": session_id
        })
        
        data = result.get("result")
        if not data:
            return f"No se encontró historial para la sesión {session_id}."
        
        messages = data.get("messages", [])
        if not messages:
            return f"La sesión {session_id} no tiene mensajes."
        
        output = f"Historial silencioso – Sesión {session_id} ({len(messages)} mensajes):\n\n"
        for msg in messages[-20:]:  # Últimos 20 mensajes para no saturar
            author = msg.get("author_id", "?")
            text = msg.get("text", "[sin texto]")
            date = msg.get("date", "")
            output += f"[{date}] Usuario {author}: {text}\n"
        
        if len(messages) > 20:
            output += f"\n... ({len(messages) - 20} mensajes anteriores omitidos)\n"
        
        return output
        
    except Exception as e:
        sys.stderr.write(f"  ❌ Error en session_history_read: {e}\n")
        return f"Error leyendo historial: {e}"
