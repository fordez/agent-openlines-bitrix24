"""
Herramienta para predecir/asignar probabilidad de cierre.
"""
from app.auth import call_bitrix_method
from tools.deal.update_deal_fields import update_deal_fields

def predict_close_probability(deal_id: str, analysis_text: str) -> str:
    """
    Estima la probabilidad de cierre basada en un análisis (del LLM) y actualiza el deal.
    
    Args:
        deal_id: ID del deal.
        analysis_text: Texto analítico o palabras clave sobre el estado del cliente.
                       Ej: "Cliente muy interesado, urge comprar" -> Alta probabilidad.
                       
    Returns:
        str: Resultado de la actualización.
    """
    if not deal_id or not analysis_text:
        return "Faltan datos"
        
    text = analysis_text.lower()
    probability = 50 # Default neutral

    if any(word in text for word in ["urgente", "seguro", "listo", "encanta", "excelente"]):
        probability = 90
    elif any(word in text for word in ["interesado", "gusta", "bueno", "posible"]):
        probability = 70
    elif any(word in text for word in ["duda", "pensar", "caro", "luego", "veremos"]):
        probability = 30
    elif any(word in text for word in ["no", "rechaza", "mal", "otro"]):
        probability = 10

    try:
        # Actualizar campo PROBABILITY (estándar en leads/deals)
        # Nota: A veces PROBABILITY es calcualdo automático por etapa en Bitrix.
        # Si falla, es porque la configuración lo impide.
        result = update_deal_fields(deal_id, {"PROBABILITY": probability})
        return f"Probabilidad calculada: {probability}% (basado en '{analysis_text}'). Resultado: {result}"
        
    except Exception as e:
        return f"Error actualizando probabilidad: {e}"
