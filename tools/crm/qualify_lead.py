"""
Herramienta para calificar leads en Bitrix24.
"""
from app.auth import call_bitrix_method

async def qualify_lead(entity_id: str, intention: str, score: int, next_action: str) -> str:
    """
    Usa esta tool para REGISTRAR la calificación de un Lead/Contacto (Intención, Score, Siguiente paso).
    El LLM debe inferir estos valores del chat y luego llamar a esta tool para guardarlos.

    Args:
        entity_id: ID del contacto/lead.
        intention: "Compra", "Duda", "Queja".
        score: 1-100.
        next_action: Qué hacer después.
    """

    comment = (
        f"🤖 **Calificación de Agente AI**\n"
        f"🔍 **Intención:** {intention}\n"
        f"⭐ **Score:** {score}\n"
        f"➡️ **Siguiente Acción:** {next_action}"
    )
    
    try:
        # Agregar comentario al timeline del contacto
        # Nota: crm.timeline.comment.add es para TIMELINE, pero a veces es mas simple crm.livefeedmessage.add
        # o simplemente actualizar COMMENTS del contacto.
        # Probaremos timeline primero.
        await call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": entity_id,
                "ENTITY_TYPE": "contact",
                "COMMENT": comment
            }
        })
        return f"Calificación registrada para contacto {entity_id}."
    except Exception as e:
        print(f"Error adding timeline comment: {e}")
        # Fallback to updating COMMENTS field just in case
        try:
             # Leer comentarios anteriores
             # No, mejor solo appending si fuera posible, pero update reemplaza.
             # Intentemos livefeed si timeline falla, o simplemente loggearlo.
             return f"Error registrando calificación en timeline: {e}"
        except:
             return "Error grave en qualification."
