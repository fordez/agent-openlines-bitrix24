
import sys
import os
from pydantic import BaseModel, Field
from app.bitrix import call_bitrix_method

async def chat_send_progress(chat_id: int, message: str, access_token: str = None, domain: str = None) -> str:
    """
    Envía un mensaje de progreso o cortesía al cliente mientas se ejecutan otras tareas.
    Sirve para mantener la interacción y reducir la sensación de espera.
    """
    params = {
        "CHAT_ID": chat_id,
        "MESSAGE": message
    }
    
    try:
        # Usamos imopenlines.bot.message.add para que el mensaje llegue correctamente al canal del cliente
        result = await call_bitrix_method("imopenlines.bot.message.add", params, access_token=access_token, domain=domain)
        return f"Mensaje de progreso enviado: {message}"
    except Exception as e:
        return f"Error al enviar mensaje de progreso: {str(e)}"
