import json
import os
import time
import asyncio

from app.base_prompt import BASE_SYSTEM_PROMPT

_DEFAULT_SYSTEM_PROMPT = BASE_SYSTEM_PROMPT

# Cache para evitar llamadas constantes a Firestore
_cached_prompt = None
_last_fetch = 0
_CACHE_TTL = 600 # 10 minutos

def _load_local_prompt():
    try:
        from agent_config import CONFIG
        return CONFIG.get("agent", {}).get("system_prompt", _DEFAULT_SYSTEM_PROMPT)
    except Exception:
        return _DEFAULT_SYSTEM_PROMPT

async def get_system_prompt() -> str:
    # Cache para evitar llamadas constantes (aunque sea local)
    global _cached_prompt, _last_fetch
    
    now = time.time()
    if _cached_prompt and (now - _last_fetch) < _CACHE_TTL:
        return _cached_prompt

    # Cargar localmente
    _cached_prompt = _load_local_prompt()
    _last_fetch = now
    return _cached_prompt

# Mantenemos esta variable por compatibilidad si algo rompe el async
SYSTEM_PROMPT = _load_local_prompt()


