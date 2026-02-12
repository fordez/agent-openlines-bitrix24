"""
Tool to update deal probability based on client interaction.
"""
from app.auth import call_bitrix_method

async def deal_update_probability_client(deal_id: int, probability: int) -> str:
    """
    Usa esta tool cuando la intención de compra del cliente cambie (ej: muestra mucho interés o pide descuento).
    Ajusta dinámicamente la probabilidad de éxito del negocio.

    Args:
        deal_id: ID del Deal.
        probability: Entero de 0 a 100 estimando la chance de cierre según la conversación.
    """
    if not deal_id or probability is None:
        return "Error: Faltan argumentos"

    try:
        if not (0 <= probability <= 100):
            return "Error: Probabilidad debe estar entre 0 y 100."

        result = await call_bitrix_method("crm.deal.update", {
            "id": deal_id,
            "fields": {"PROBABILITY": probability}
        })
        
        if result.get("result"):
             return f"Probabilidad actualizada a {probability}% en Deal {deal_id}."
        else:
             return "No se pudo actualizar la probabilidad."
             
    except Exception as e:
        return f"Error actualizando probabilidad: {e}"
