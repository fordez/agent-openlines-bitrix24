import asyncio
import os
import sys
from datetime import datetime

# Añadir el path raíz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.context_vars import member_id_var
from app.token_manager import get_token_manager
from app.redis_client import get_redis

async def test_multitenant_context():
    print("🧪 Probando Multi-Tenancy en TokenManager...")
    tm = await get_token_manager()
    
    # 1. Probar context_var
    token = member_id_var.set("tenant_123")
    resolved_id = await tm.get_member_id()
    print(f"  ✅ ContextVar resolved: {resolved_id}")
    assert resolved_id == "tenant_123"
    member_id_var.reset(token)

    # 2. Probar mapping chat_id -> member_id
    r = await get_redis()
    await r.set("map:chat_to_member:999", "tenant_456", ex=60)
    
    resolved_id_from_chat = await tm.get_member_id_from_chat(999)
    print(f"  ✅ Redis map resolved: {resolved_id_from_chat}")
    assert resolved_id_from_chat == "tenant_456"

    print("🚀 Pruebas de lógica básica EXITOSAS")

if __name__ == "__main__":
    asyncio.run(test_multitenant_context())
