"""
Cliente Redis singleton para compartir conexión entre módulos.
Usa REDIS_URL del entorno o fallback a localhost.
"""
import os
import redis.asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """Retorna el cliente Redis singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            REDIS_URL,
            decode_responses=True,
            max_connections=20,
        )
    return _redis_client


async def close_redis():
    """Cierra la conexión Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
