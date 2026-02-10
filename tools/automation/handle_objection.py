"""
Herramienta para gestionar objeciones comerciales.
"""
from app.auth import call_bitrix_method
from tools.deal.add_deal_note import add_deal_note

def handle_objection(deal_id: str, objection: str, response_strategy: str) -> str:
    """
    Registra una objeción del cliente y la estrategia usada para responderla.
    Útil para análisis posterior y entrenamiento.
    
    Args:
        deal_id: ID del deal.
        objection: La objeción del cliente (ej: "Es muy caro").
        response_strategy: La respuesta dada (ej: "Ofrecí descuento del 10%").
        
    Returns:
        str: Resultado del registro.
    """
    if not deal_id:
        return "Falta deal_id"

    note_content = (
        f"🛑 **Objeción Detectada**\n"
        f"🗣️ Cliente: {objection}\n"
        f"🛡️ Respuesta: {response_strategy}"
    )
    
    return add_deal_note(deal_id, note_content)
