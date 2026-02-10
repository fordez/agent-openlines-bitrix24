"""
Herramienta para vincular un chat de Open Lines al CRM creando un Lead.
Usa el método: imopenlines.crm.lead.create
"""
from app.auth import call_bitrix_method


def crm_chat_link(chat_id: str) -> str:
    """
    Vincula una conversación de Open Lines al CRM creando un Lead automáticamente.
    Bitrix24 asocia el chat al nuevo Lead, permitiendo dar seguimiento desde el CRM.

    Args:
        chat_id: ID del chat de Open Lines a vincular al CRM.

    Returns:
        str: Mensaje con el ID del Lead creado o error.
    """
    if not chat_id:
        return "Error: chat_id es requerido."

    try:
        result = call_bitrix_method("imopenlines.crm.lead.create", {
            "CHAT_ID": chat_id,
        })
        if result.get("result"):
            lead_id = result["result"]
            return f"Chat {chat_id} vinculado al CRM exitosamente. Lead creado con ID: {lead_id}."
        else:
            error = result.get("error_description", result)
            return f"Error al vincular chat al CRM: {error}"
    except Exception as e:
        return f"Error al vincular chat al CRM: {e}"
