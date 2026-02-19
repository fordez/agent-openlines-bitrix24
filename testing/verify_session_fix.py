
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Redis to avoid side effects
mock_redis = MagicMock()
mock_redis.lock = MagicMock()
mock_lock = AsyncMock()
mock_redis.lock.return_value = mock_lock

async def verify_fix():
    print("🧪 Verifying session creation fix...")
    
    # Mock imports that depend on environment/external services
    with patch('app.sessions.get_firestore_config') as mock_fs, \
         patch('app.sessions.get_redis', return_value=AsyncMock()), \
         patch('app.sessions.clear_chat_history', new_callable=AsyncMock) as mock_clear, \
         patch('app.sessions.Agent') as mock_agent_class, \
         patch('app.sessions.app') as mock_app:
        
        # Setup mocks
        mock_fs_instance = AsyncMock()
        mock_fs.return_value = mock_fs_instance
        mock_fs_instance.get_tenant_config.return_value = {
            "model": "gpt-4o",
            "temperature": "0.7",
            "provider": "openai"
        }
        
        mock_agent = MagicMock()
        mock_agent.attach_llm = AsyncMock()
        mock_agent_class.return_value = mock_agent
        
        from app.sessions import create_new_session
        
        print("Running create_new_session...")
        try:
            session = await create_new_session("chat_test_123")
            print("✅ create_new_session completed without TypeError!")
            
            # Verify partial was used (conceptually, by checking if attach_llm was called with llm_factory)
            args, kwargs = mock_agent.attach_llm.call_args
            if 'llm_factory' in kwargs:
                print("✅ llm_factory was passed to attach_llm!")
                factory = kwargs['llm_factory']
                print(f"Factory: {factory}")
            else:
                print("❌ llm_factory was NOT found in attach_llm call!")
                
        except TypeError as e:
            print(f"❌ TypeError caught: {e}")
        except Exception as e:
            print(f"⚠️ Unexpected error: {e}")
            import traceback
            traceback.print_exc()

    print("\n🧪 Verifying Redis lock safety...")
    with patch('app.redis_client.get_redis') as mock_get_redis:
        r = AsyncMock()
        mock_get_redis.return_value = r
        
        from app.memory import clear_chat_history
        await clear_chat_history("chat_test_123")
        
        # Verify that we did NOT call delete on the lock key
        lock_key = "lock:chat:chat_test_123"
        delete_calls = [call.args[0] for call in r.delete.call_args_list]
        if lock_key in delete_calls:
            print(f"❌ ERROR: clear_chat_history is still deleting the lock key: {lock_key}")
        else:
            print(f"✅ clear_chat_history did NOT delete the lock key. Lock is safe!")

if __name__ == "__main__":
    asyncio.run(verify_fix())
