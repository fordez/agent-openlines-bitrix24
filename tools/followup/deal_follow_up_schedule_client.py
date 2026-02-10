"""
Tool to schedule automatic follow up for date.
"""
from app.auth import call_bitrix_method
from datetime import datetime, timedelta

async def deal_follow_up_schedule_client(deal_id: int, interaction_type: str, time_offset_hours: int = 24) -> str:
    """
    Usa esta tool para PROGRAMAR un seguimiento si el cliente pide "hablamos mañana" o queda pendiente algo.
    Deja una marca en el timeline para retomar contacto futuro.

    Args:
        deal_id: ID del Deal.
        interaction_type: Motivo del seguimiento (ej: "Revisar decisión", "Llamar mañana").
        time_offset_hours: En cuantas horas realizar el seguimiento.
    """
    if not deal_id or not interaction_type:
        return "Error: Faltan argumentos"

    try:
        # Fallback to timeline comment
        full_comment = f"⏰ **SEGUIMIENTO PROGRAMADO**\nMotivo: {interaction_type}\nOffset: Dentro de {time_offset_hours}hs"
        
        result = await call_bitrix_method("crm.timeline.comment.add", {
            "fields": {
                "ENTITY_ID": deal_id,
                "ENTITY_TYPE": "deal",
                "COMMENT": full_comment
            }
        })
        
        if result.get("result"):
             return f"Seguimiento registrado en timeline del Deal {deal_id}."
        else:
             return "No se pudo registrar el seguimiento."
             
    except Exception as e:
        return f"Error registrando seguimiento: {e}"
