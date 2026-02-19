
import asyncio
import os
from mcp.client.stdio import StdioServerParameters, get_default_environment

# Mock the config dictionary that would come from the YAML
mock_config_env = {
    "REDIS_URL": "${REDIS_URL}",
    "BITRIX_DOMAIN": "hardcoded_domain"
}

# Set the actual env var
os.environ["REDIS_URL"] = "redis://verified:6379/0"

async def test_env_resolution():
    print("Testing environment variable resolution in StdioServerParameters...")
    
    # In mcp_connection_manager.py line 452:
    # env={**get_default_environment(), **(config.env or {})},
    
    # If the YAML parser doesn't expand ${REDIS_URL}, then config.env['REDIS_URL'] will be literally "${REDIS_URL}"
    # and passed as such to the subprocess.
    
    # Python's os.path.expandvars could be used but isn't used in mcp_connection_manager.py
    # This implies that the expansion MUST happen at the configuration loading stage (e.g. via Hydra or OmniConf if used)
    # OR that it doesn't happen at all.
    
    resolved_env = {**get_default_environment(), **mock_config_env}
    
    print(f"Value of REDIS_URL passed to subprocess: {resolved_env.get('REDIS_URL')}")
    
    if resolved_env.get('REDIS_URL') == "redis://verified:6379/0":
        print("✅ Resolution happened (Likely by Config Loader upstream)")
    elif resolved_env.get('REDIS_URL') == "${REDIS_URL}":
        print("❌ Resolution DID NOT happen. The subprocess will receive the literal string '${REDIS_URL}'.")
        print("⚠️  Action Required: We must likely use a shell wrapper or find a way to make the config loader expand vars.")
    else:
        print(f"❓ Unexpected value: {resolved_env.get('REDIS_URL')}")

if __name__ == "__main__":
    asyncio.run(test_env_resolution())
