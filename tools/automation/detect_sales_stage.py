"""
Herramienta para detectar y actualizar la etapa de venta basada en la conversación.
"""
from app.auth import call_bitrix_method
from tools.deal.update_deal_stage import update_deal_stage

def detect_sales_stage(deal_id: str, last_message: str) -> str:
    """
    Analiza el último mensaje del cliente y actualiza la etapa del deal si detecta intenciones claras.
    
    Args:
        deal_id: ID del deal.
        last_message: Texto del último mensaje del usuario.
        
    Returns:
        str: Resultado de la detección y actualización.
    """
    if not deal_id or not last_message:
        return "Faltan datos (deal_id, last_message)"

    msg = last_message.lower()
    new_stage = None
    reason = ""

    # Lógica heurística simple (personalizable)
    if any(word in msg for word in ["compro", "lo quiero", "reservar", "pago", "tarjeta"]):
        new_stage = "WON" # O una etapa previa como "INVOICING"
        reason = "Intención de compra detectada"
    elif any(word in msg for word in ["precio", "cuánto", "cotización", "presupuesto"]):
        new_stage = "PREPARATION" # O "PROPOSAL"
        reason = "Solicitud de presupuesto"
    elif any(word in msg for word in ["info", "detalles", "duda", "pregunta"]):
        new_stage = "NEW" # O mantener
        reason = "Solicitud de información"

    if new_stage:
        # Llamamos a la herramienta existente para actualizar
        # Nota: 'WON' suele requerir cerrar el deal, update_deal_stage debería manejarlo o usamos close_deal
        # Por simplicidad, intentamos moverlo a la etapa. Si es WON, update_deal_stage podría fallar si bitrix exige campos obligatorios.
        # Asumimos etapas intermedias por ahora.
        
        try:
            result = update_deal_stage(deal_id, new_stage)
            return f"Etapa detectada: {new_stage} ({reason}). Resultado: {result}"
        except Exception as e:
            return f"Error actualizando etapa detectada: {e}"
            
    return "No se detectó cambio de etapa necesario."
