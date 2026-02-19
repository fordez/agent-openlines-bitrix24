from mcp_agent.app import MCPApp
import asyncio

MCP_SERVER_NAME = "bitrix_crm"
app = MCPApp(name="bot_viajes_agent") # Constructor no acepta server_names=[] en esta versión

_agent_app_instance = None
_app_context_manager = None

async def get_agent_app():
    """Retorna la instancia global del AgentApp, iniciándola si es necesario."""
    global _agent_app_instance, _app_context_manager
    if _agent_app_instance is None:
        print("🚀 [Context] Iniciando MCP AgentApp global...")
        _app_context_manager = app.run()
        _agent_app_instance = await _app_context_manager.__aenter__()
    return _agent_app_instance

async def close_agent_app():
    """Cierra el AgentApp global al apagar el servidor."""
    global _agent_app_instance, _app_context_manager
    if _app_context_manager:
        print("🛑 [Context] Cerrando MCP AgentApp...")
        await _app_context_manager.__aexit__(None, None, None)
        _agent_app_instance = None
        _app_context_manager = None
