
import asyncio
import os
from mcp_agent.app import MCPApp
from mcp_agent.config import load_config

# Set dummy env vars for testing
os.environ["REDIS_URL"] = "redis://test:6379/0"
os.environ["BITRIX_DOMAIN"] = "test.bitrix24.es"

async def verify_config_loading():
    print("Loading MCP App to check config expansion...")
    try:
        # We just want to see if the config loader parses ${VAR}
        # mcp-agent uses Hydra or similar usually, let's see how it behaves via MCPApp
        # or we can inspect the internal config loading mechanism if accessible.
        # Since MCPApp loads config internally, we might just try to instantiate it and see if it fails
        # or if we can inspect its configuration.
        
        app = MCPApp(name="test_agent", config_path="mcp_agent.config.yaml")
        print("MCPApp initialized.")
        
        # Accessing the config object if possible
        if hasattr(app, 'config'):
            print(f"Config object found: {type(app.config)}")
            # This depends on the internal structure of MCPApp. 
            # Let's inspect 'mcp.servers' in the config if exposed
            if hasattr(app.config, 'mcp') and hasattr(app.config.mcp, 'servers'):
                 servers = app.config.mcp.servers
                 if 'bitrix_crm' in servers:
                     srv = servers['bitrix_crm']
                     print(f"Server config for bitrix_crm: {srv}")
                     if 'env' in srv:
                         print(f"Env vars: {srv['env']}")
                         if srv['env'].get('REDIS_URL') == "redis://test:6379/0":
                             print("✅ Env var expansion SUCCESSFUL")
                         elif srv['env'].get('REDIS_URL') == "${REDIS_URL}":
                             print("❌ Env var expansion FAILED (Raw string returned)")
                         else:
                             print(f"❓ Unexpected value: {srv['env'].get('REDIS_URL')}")
                     else:
                         print("❌ 'env' section not found in server config")
        else:
            print("Could not access app.config directly.")

    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    asyncio.run(verify_config_loading())
