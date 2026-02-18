import asyncio
import os
import json
from app.firestore_config import get_firestore_config
from app.redis_client import get_redis
from app.sessions import create_new_session

async def test_integration():
    print("🧪 Iniciando test de integración...")
    
    # Setup mock env
    tenant_id = "test_tenant_123"
    os.environ["BITRIX_MEMBER_ID"] = tenant_id
    
    redis = await get_redis()
    fs = await get_firestore_config()
    
    # 1. Test get_tenant_config (Fallback case)
    print("1. Buscando config inexistente (debe usar default)...")
    config = await fs.get_tenant_config("non_existent")
    if config is None:
        print("  ✅ Fallback correcto.")
    
    # 2. Test session creation and cleanup
    print("2. Creando sesión y verificando limpieza de Redis...")
    chat_id = "test_chat_sh456"
    await redis.set(f"chat:{chat_id}:history", "old_garbage")
    
    session = await create_new_session(chat_id)
    history = await redis.get(f"chat:{chat_id}:history")
    
    if history is None:
        print("  ✅ Redis limpiado al iniciar sesión.")
    else:
        print("  ❌ Redis NO se limpió.")

    print("\n🚀 Test finalizado. Nota: El listener de Firestore requiere credenciales reales para ser probado.")

if __name__ == "__main__":
    asyncio.run(test_integration())
