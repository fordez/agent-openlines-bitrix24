import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import auth

async def list_recent_chats():
    print("--- Listando Chats Recientes ---")
    try:
        # Probamos con im.chat.list si existe o similar
        result = await auth.call_bitrix_method("im.chat.list", {})
        print(f"Chats: {result}")
    except Exception as e:
        print(f"Error listando chats: {e}")

if __name__ == "__main__":
    asyncio.run(list_recent_chats())
