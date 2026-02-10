"""
Módulo de memoria simple y persistente (JSON).
Guarda los últimos N mensajes por chat_id.
"""
import json
import os
from typing import List, Dict

MEMORY_FILE = "conversation_history.json"
MAX_HISTORY = 10

def load_all_history() -> Dict[str, List[dict]]:
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_all_history(history: Dict[str, List[dict]]):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def get_chat_history(chat_id: str) -> List[dict]:
    """Retorna la lista de mensajes (role, content) para un chat."""
    data = load_all_history()
    return data.get(str(chat_id), [])

def add_message(chat_id: str, role: str, content: str):
    """Guarda un mensaje y mantiene el límite de historial."""
    chat_id = str(chat_id)
    data = load_all_history()
    
    if chat_id not in data:
        data[chat_id] = []
    
    # Agregar nuevo mensaje
    data[chat_id].append({"role": role, "content": content})
    
    # Recortar si excede el máximo
    if len(data[chat_id]) > MAX_HISTORY:
        data[chat_id] = data[chat_id][-MAX_HISTORY:]
        
    save_all_history(data)

def format_history_str(chat_id: str) -> str:
    """Retorna el historial como texto formateado para el prompt."""
    history = get_chat_history(chat_id)
    if not history:
        return ""
    
    output = "\n--- HISTORIAL DE CONVERSACIÓN RECIENTE ---\n"
    for msg in history:
        role_label = "Cliente" if msg['role'] == 'user' else "Bot Viajes"
        output += f"{role_label}: {msg['content']}\n"
    output += "--- FIN HISTORIAL ---\n"
    return output


def get_seed_messages(chat_id: str, max_messages: int = 6) -> list:
    """
    Retorna los últimos N mensajes formateados como lista de dicts
    para sembrar una nueva sesión de agente después de expiración TTL.
    
    Returns:
        Lista de dicts con 'role' y 'content'.
    """
    history = get_chat_history(chat_id)
    if not history:
        return []
    return history[-max_messages:]

