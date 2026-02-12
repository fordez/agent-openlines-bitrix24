"""
Tool to get queue configuration info for an Open Line.
"""
from app.auth import call_bitrix_method
import sys

async def session_queue_info(config_id: int = 1) -> str:
    """
    Consulta la configuración de la cola de atención de una línea abierta.
    Devuelve el tiempo de rotación por agente (QUEUE_TIME) y el tamaño de la cola.
    
    Args:
        config_id: ID de la configuración de Open Line (por defecto 1).
    """
    sys.stderr.write(f"  🔍 Tool session_queue_info: config_id={config_id}\n")
    
    try:
        result = await call_bitrix_method("imopenlines.config.get", {
            "CONFIG_ID": config_id,
            "WITH_QUEUE": "Y",
            "SHOW_OFFLINE": "N"
        })
        
        data = result.get("result")
        if not data:
            return "No se pudo obtener la configuración de la línea."
        
        line_name = data.get("LINE_NAME", "Sin nombre")
        queue_time = data.get("QUEUE_TIME", "N/A")
        no_answer_time = data.get("NO_ANSWER_TIME", "N/A")
        queue = data.get("QUEUE", [])
        online_count = len(queue)
        
        output = f"Info de Cola – Línea: {line_name}\n"
        output += f"- Operadores online: {online_count}\n"
        output += f"- Tiempo de rotación por agente: {queue_time} segundos\n"
        output += f"- Tiempo máx. sin respuesta: {no_answer_time} segundos\n"
        
        if online_count > 0:
            estimated_max = int(queue_time) * online_count if str(queue_time).isdigit() else "N/A"
            output += f"- Tiempo estimado máximo de espera: ~{estimated_max} segundos\n"
        else:
            output += "- ⚠️ No hay operadores online. Considerar no transferir.\n"
        
        return output
        
    except Exception as e:
        sys.stderr.write(f"  ❌ Error en session_queue_info: {e}\n")
        return f"Error consultando cola: {e}"
