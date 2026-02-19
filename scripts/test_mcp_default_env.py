
import os
from mcp.client.stdio import get_default_environment

print("Testing get_default_environment()...")
env = get_default_environment()

if "REDIS_URL" in env:
     print(f"✅ REDIS_URL found in default env: {env['REDIS_URL']}")
else:
     print("❌ REDIS_URL NOT found in default env")

if "PATH" in env:
     print("✅ PATH found (sanity check)")
