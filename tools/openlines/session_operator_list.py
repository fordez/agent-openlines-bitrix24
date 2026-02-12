"""
Tool to list online operators for an Open Line using imopenlines.config.get.
"""
from app.auth import call_bitrix_method
import sys

async def session_operator_list(config_id: int = 1) -> str:
    """
    Lista los operadores asignados a la línea abierta que están ONLINE.
    Usa imopenlines.config.get con SHOW_OFFLINE=N.
    
    Args:
        config_id: ID de la configuración de Open Line (por defecto 1).
    """
    sys.stderr.write(f"  🔍 Tool session_operator_list: config_id={config_id}\n")
    
    try:
        result = await call_bitrix_method("imopenlines.config.get", {
            "CONFIG_ID": config_id,
            "WITH_QUEUE": "Y",
            "SHOW_OFFLINE": "N"
        })
        
        data = result.get("result")
        if not data:
            return "No se pudo obtener la configuración de la línea abierta."
        
        queue = data.get("QUEUE", [])
        line_name = data.get("LINE_NAME", "Sin nombre")
        queue_time = data.get("QUEUE_TIME", "N/A")
        
        if not queue:
            return f"Línea '{line_name}': No hay operadores online en este momento."
        
        output = f"Línea: {line_name} | Tiempo por rotación: {queue_time}s\nOperadores online:\n"
        for op in queue:
            user_id = op.get("USER_ID", op) if isinstance(op, dict) else op
            output += f"- Usuario ID: {user_id}\n"
        
        return output
        
    except Exception as e:
        sys.stderr.write(f"  ❌ Error en session_operator_list: {e}\n")
        return f"Error listando operadores: {e}"
