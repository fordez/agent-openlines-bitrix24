import asyncio
import time
import psutil
import os
from datetime import datetime
from firebase_admin import firestore
import sys

# Redirect all prints to stderr to avoid breaking MCP protocol
_print = print
def print(*args, **kwargs):
    kwargs.setdefault('file', sys.stderr)
    _print(*args, **kwargs)

from app.firestore_config import get_firestore_config

class MetricsService:
    _instance = None
    _db = None

    def __init__(self):
        # El cliente de Firestore ya debería estar inicializado en firestore_config
        # Pero aseguramos obtener la instancia del servicio de config para reutilizar la conexión si es posible,
        # o inicializar uno nuevo si no hay.
        self._db = firestore.client()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            # Asegurar que firestore esté inicializado
            await get_firestore_config()
            cls._instance = cls()
        return cls._instance

    async def log_token_usage(self, tenant_id: str, prompt_tokens: int, completion_tokens: int, model: str, cost: float = 0.0):
        """Registra el consumo de tokens en Firestore de forma asíncrona."""
        if not tenant_id:
            return

        asyncio.create_task(self._log_token_usage_async(tenant_id, prompt_tokens, completion_tokens, model, cost))

    async def _log_token_usage_async(self, tenant_id: str, prompt_tokens: int, completion_tokens: int, model: str, cost: float):
        try:
            timestamp = datetime.now()
            doc_data = {
                "tenantId": tenant_id,
                "metricType": "tokens",
                "promptTokens": prompt_tokens,
                "completionTokens": completion_tokens,
                "totalTokens": prompt_tokens + completion_tokens,
                "model": model,
                "cost": cost,
                "timestamp": timestamp
            }
            # Guardar en colección particionada por fecha o general 'metrics'
            # Para simplificar, usamos una colección 'metrics'
            self._db.collection('metrics').add(doc_data)
        except Exception as e:
            print(f"❌ Error logging token usage: {e}")

    async def log_tool_usage(self, tenant_id: str, tool_name: str, success: bool, duration_ms: float):
        """Registra la ejecución de una herramienta."""
        if not tenant_id:
            tenant_id = "unknown"

        asyncio.create_task(self._log_tool_usage_async(tenant_id, tool_name, success, duration_ms))

    async def _log_tool_usage_async(self, tenant_id: str, tool_name: str, success: bool, duration_ms: float):
        try:
            timestamp = datetime.now()
            doc_data = {
                "tenantId": tenant_id,
                "metricType": "tool_usage",
                "toolName": tool_name,
                "success": success,
                "durationMs": duration_ms,
                "timestamp": timestamp
            }
            self._db.collection('metrics').add(doc_data)
        except Exception as e:
            print(f"❌ Error logging tool usage: {e}")

    async def start_system_metrics_logger(self, interval_seconds: int = 60):
        """Inicia un loop en background para loguear CPU/RAM."""
        asyncio.create_task(self._system_metrics_loop(interval_seconds))

    async def _system_metrics_loop(self, interval: int):
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                doc_data = {
                    "tenantId": "system",
                    "metricType": "system_health",
                    "cpuPercent": cpu_percent,
                    "memoryPercent": memory.percent,
                    "memoryUsedMb": memory.used / (1024 * 1024),
                    "timestamp": datetime.now()
                }
                self._db.collection('metrics').add(doc_data)
            except Exception as e:
                print(f"❌ Error logging system metrics: {e}")
            
            await asyncio.sleep(interval)
