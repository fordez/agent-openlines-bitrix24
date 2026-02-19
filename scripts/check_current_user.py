import asyncio
import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.getcwd())

from app.auth import call_bitrix_method

async def check_user():
    print("Obteniendo información del usuario actual...")
    try:
        # El método 'user.current' retorna el usuario del token actual
        res = await call_bitrix_method("user.current")
        user = res.get("result", {})
        print(f"✅ Usuario detectado: {user.get('NAME')} {user.get('LAST_NAME')} (ID: {user.get('ID')})")
        print(f"📧 Email: {user.get('EMAIL')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(check_user())
