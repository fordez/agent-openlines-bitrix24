from mcp_agent.app import MCPApp
from dotenv import load_dotenv

load_dotenv()

MCP_SERVER_NAME = "bitrix_crm"
TRAVEL_SERVER_NAME = "travel_intel"
app = MCPApp(name="bot_viajes_agent")
