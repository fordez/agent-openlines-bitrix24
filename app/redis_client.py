"""
Cliente Redis singleton para compartir conexión entre módulos.
Usa REDIS_URL del entorno o fallback a localhost.
"""
import os
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_client: aioredis.Redis | None = None


class MockRedis:
    """Mock Redis para entornos sin servidor Redis."""
    def __init__(self):
        self._data = {}
    async def get(self, key):
        return self._data.get(key)
    async def set(self, key, value):
        self._data[key] = value
        return True
    async def aclose(self):
        pass

async def get_redis() -> aioredis.Redis:
    """Retorna el cliente Redis singleton con fallback a MockRedis."""
    global _redis_client
    if _redis_client is None:
        try:
            client = aioredis.from_url(
                REDIS_URL,
                decode_responses=True,
                max_connections=20,
            )
            # Verificar conexión rápida
            await client.ping()
            _redis_client = client
            print("  ✅ Conectado a Redis Real")
        except Exception as e:
            print(f"  ⚠️ Redis no disponible ({e}). Usando MockRedis.")
            _redis_client = MockRedis()
    return _redis_client

async def close_redis():
    """Cierra la conexión Redis."""
    global _redis_client
    if _redis_client is not None:
        if hasattr(_redis_client, 'aclose'):
            await _redis_client.aclose()
        _redis_client = None
