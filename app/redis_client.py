"""
Cliente Redis singleton para compartir conexión entre módulos.
Usa REDIS_URL del entorno o fallback a localhost.
"""
import os
import sys
import asyncio
import time
import redis.asyncio as aioredis

# Redirect all prints to stderr to avoid breaking MCP protocol
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_client: aioredis.Redis | None = None


class MockRedis:
    """Mock Redis para entornos sin servidor Redis."""
    def __init__(self):
        self._data = {}
    async def get(self, key):
        return self._data.get(key)
    async def set(self, key, value, **kwargs):
        self._data[key] = value
        return True
    async def aclose(self):
        pass

from datetime import datetime

def log(msg: str):
    now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{now}] {msg}")

async def get_redis() -> aioredis.Redis:
    """Retorna el cliente Redis singleton con socket timeout para evitar bloqueos."""
    global _redis_client
    if _redis_client is None:
        try:
            log(f"🔗 Intentando conectar a Redis: {REDIS_URL}")
            client = aioredis.from_url(
                REDIS_URL,
                decode_responses=True,
                max_connections=20,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=False
            )
            # Verificar conexión con timeout real
            await asyncio.wait_for(client.ping(), timeout=2.5)
            _redis_client = client
            log("✅ Conexión a Redis exitosa")
        except Exception as e:
            log(f"⚠️ Redis no disponible ({type(e).__name__}: {e}). Usando MockRedis.")
            _redis_client = MockRedis()
    return _redis_client

async def close_redis():
    """Cierra la conexión Redis."""
    global _redis_client
    if _redis_client is not None:
        if hasattr(_redis_client, 'aclose'):
            await _redis_client.aclose()
        _redis_client = None
