"""
Módulo de memoria persistente (JSON) con I/O asíncrono.
Guarda los últimos N mensajes por chat_id sin bloquear el event loop.
"""
import json
import os
import asyncio
import aiofiles
from typing import List, Dict

MEMORY_FILE = "conversation_history.json"
MAX_HISTORY = 10

_memory_lock = asyncio.Lock()


async def load_all_history() -> Dict[str, List[dict]]:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        async with aiofiles.open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content) if content.strip() else {}
    except Exception:
        return {}


async def save_all_history(history: Dict[str, List[dict]]):
    async with aiofiles.open(MEMORY_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(history, ensure_ascii=False, indent=2))


async def get_chat_history(chat_id: str) -> List[dict]:
    """Retorna la lista de mensajes (role, content) para un chat."""
    data = await load_all_history()
    return data.get(str(chat_id), [])


async def add_message(chat_id: str, role: str, content: str):
    """Guarda un mensaje y mantiene el límite de historial."""
    async with _memory_lock:
        chat_id = str(chat_id)
        data = await load_all_history()

        if chat_id not in data:
            data[chat_id] = []

        data[chat_id].append({"role": role, "content": content})

        if len(data[chat_id]) > MAX_HISTORY:
            data[chat_id] = data[chat_id][-MAX_HISTORY:]

        await save_all_history(data)


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
    Retorna los últimos N mensajes formateados como lista de dicts
    para sembrar una nueva sesión de agente después de expiración TTL.
    """
    history = await get_chat_history(chat_id)
    if not history:
        return []
    return history[-max_messages:]
