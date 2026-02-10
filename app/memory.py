"""
Módulo de memoria persistente usando Redis.
Guarda los últimos N mensajes por chat_id con TTL automático.
"""
import json
from typing import List, Dict
from app.redis_client import get_redis

MAX_HISTORY = 10
HISTORY_TTL = 60 * 60 * 24 * 7  # 7 días


def _key(chat_id: str) -> str:
    """Genera la clave Redis para un chat."""
    return f"chat:{chat_id}:history"


async def get_chat_history(chat_id: str) -> List[dict]:
    """Retorna la lista de mensajes (role, content) para un chat."""
    r = await get_redis()
    messages = await r.lrange(_key(chat_id), 0, -1)
    return [json.loads(m) for m in messages]


async def add_message(chat_id: str, role: str, content: str):
    """Guarda un mensaje y mantiene el límite de historial."""
    r = await get_redis()
    key = _key(chat_id)
    msg = json.dumps({"role": role, "content": content}, ensure_ascii=False)

    pipe = r.pipeline()
    pipe.rpush(key, msg)
    pipe.ltrim(key, -MAX_HISTORY, -1)
    pipe.expire(key, HISTORY_TTL)
    await pipe.execute()


async def format_history_str(chat_id: str) -> str:
    """Retorna el historial como texto formateado para el prompt."""
    history = await get_chat_history(chat_id)
    if not history:
        return ""

    output = "\n--- HISTORIAL DE CONVERSACIÓN RECIENTE ---\n"
    for msg in history:
        role_label = "Cliente" if msg['role'] == 'user' else "Bot Viajes"
        output += f"{role_label}: {msg['content']}\n"
    output += "--- FIN HISTORIAL ---\n"
    return output


async def get_seed_messages(chat_id: str, max_messages: int = 6) -> list:
    """
    Retorna los últimos N mensajes para sembrar una nueva sesión
    de agente después de expiración TTL.
    """
    history = await get_chat_history(chat_id)
    if not history:
        return []
    return history[-max_messages:]
