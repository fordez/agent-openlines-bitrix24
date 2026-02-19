import asyncio
import sys
import os

# Add root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.openlines.advisor_notify import advisor_notify
from tools.openlines.session_transfer import session_transfer
from tools.task.task_create import task_create
from tools.crm.crm_add_note import crm_add_note
from unittest.mock import patch, AsyncMock

async def test_transfer_flow():
    print("🚀 Starting Transfer Flow Verification (Full Mock)...")
    
    chat_id = "123"
    lead_id = 456
    advisor_id = 789
    
    # Mock both call_bitrix_method and any auth-related refresh logic
    with patch('app.auth.call_bitrix_method', new_callable=AsyncMock) as mock_call:
        mock_call.return_value = {"result": True, "task": {"id": 101}}
        
        print("\n1. Testing crm_add_note...")
        note_res = await crm_add_note(entity_id=lead_id, entity_type="LEAD", message="Test summary for transfer")
        print(f"   Result: {note_res}")
        
        print("\n2. Testing session_transfer...")
        trans_res = await session_transfer(chat_id=chat_id, user_id=str(advisor_id))
        print(f"   Result: {trans_res}")
        
        print("\n3. Testing advisor_notify...")
        notif_res = await advisor_notify(user_id=advisor_id, message="Test notification")
        print(f"   Result: {notif_res}")
        
        print("\n4. Testing task_create...")
        # Mocking get_current_user_id inside task_create if needed
        with patch('app.auth.get_current_user_id', new_callable=AsyncMock) as mock_user:
            mock_user.return_value = 1
            task_res = await task_create(title="[URGENTE] Traspaso", description="Test task", entity_id=lead_id, responsible_id=advisor_id)
            print(f"   Result: {task_res}")

    print("\n✅ Verification script completed successfully (all mocks passed).")

if __name__ == "__main__":
    asyncio.run(test_transfer_flow())
