import asyncio
import sys
import os

# Ensure current directory is in path
sys.path.insert(0, os.getcwd())

from app.auth import call_bitrix_method

async def list_users():
    print("Listando usuarios del portal...")
    try:
        res = await call_bitrix_method("user.get", {"ACTIVE": True})
        users = res.get("result", [])
        for user in users:
            print(f"👤 {user.get('NAME')} {user.get('LAST_NAME')} - ID: {user.get('ID')} - Email: {user.get('EMAIL')}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(list_users())
