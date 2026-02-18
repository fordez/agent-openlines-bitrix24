import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Mock firebase_admin BEFORE importing app modules
sys.modules['firebase_admin'] = MagicMock()
sys.modules['firebase_admin.credentials'] = MagicMock()
sys.modules['firebase_admin.firestore'] = MagicMock()

# Mock get_redis too since MetricsService might use it indirectly via FirestoreConfig?
# Actually app.metrics only uses firestore.client() directly in __init__
# But get_instance calls get_firestore_config
# Let's mock app.firestore_config to avoid complex dependencies
sys.modules['app.firestore_config'] = MagicMock()

from app.metrics import MetricsService

async def verify_metrics():
    print("🧪 Verifying Metrics Collection (MOCKED)...")
    
    # Create a mock for the Firestore client
    mock_firestore_client = MagicMock()
    mock_collection = MagicMock()
    mock_firestore_client.collection.return_value = mock_collection
    
    # Instantiate MetricsService directly (bypassing get_instance to avoid side effects)
    # We override _db manually
    ms = MetricsService()
    ms._db = mock_firestore_client
    
    # 2. Log Token Usage
    print("  📝 Logging Token Usage...")
    await ms.log_token_usage("test-tenant", 10, 20, "test-model", 0.001)
    
    # 3. Log Tool Usage
    print("  📝 Logging Tool Usage...")
    await ms.log_tool_usage("test-tenant", "test_tool", True, 150.5)
    
    # 4. Wait for async tasks
    await asyncio.sleep(0.1)
    
    # 5. Verify calls
    print("  🔍 Verifying Firestore calls...")
    
    calls = mock_collection.add.call_args_list
    print(f"    Calls to add(): {len(calls)}")
    
    found_token = False
    found_tool = False
    
    for call in calls:
        args, kwargs = call
        data = args[0]
        print(f"    📄 Logged: {data.get('metricType')} - {data.get('tenantId')}")
        
        if data.get('metricType') == 'tokens' and data.get('tenantId') == 'test-tenant':
            found_token = True
            if data.get('promptTokens') == 10 and data.get('completionTokens') == 20:
                print("      ✅ Token counts match")
                
        if data.get('metricType') == 'tool_usage' and data.get('tenantId') == 'test-tenant':
            found_tool = True
            if data.get('toolName') == 'test_tool' and data.get('success') is True:
                 print("      ✅ Tool data matches")
            
    if found_token and found_tool:
        print("✅ SUCCESS: Metrics verification passed (MOCKED)!")
    else:
        print("❌ FAILURE: Mock calls missing.")

if __name__ == "__main__":
    asyncio.run(verify_metrics())
