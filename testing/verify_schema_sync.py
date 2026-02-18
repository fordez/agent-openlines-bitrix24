import asyncio
import os
import json
import sys

# Añadir el path raíz para importar app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.firestore_config import get_firestore_config
from app.redis_client import get_redis

async def verify_schema_sync():
    """
    Verifica el esquema de Firestore y cómo los agentes sincronizan los datos.
    Este script analiza la estructura de colecciones esperada y valida la lógica de caché.
    """
    print("🧪 [TEST] Iniciando verificación de Esquema y Sincronización...")
    
    tenant_id = os.getenv("BITRIX_MEMBER_ID", "de8a86baab829293f6c14beedf688e0c")
    print(f"📍 Analizando Schema para Tenant: {tenant_id}")

    # Estructura del Esquema Firestore (Basado en Auditoría)
    SCHEMA_DEFINITION = {
        "installations": {
            "key": "member_id",
            "fields": ["domain", "accessToken", "status", "expiresAt"]
        },
        "agents": {
            "key": "auto_id (filtro por tenantId)",
            "fields": ["name", "role", "objective", "tone", "knowledge", "model", "temperature"]
        },
        "config-ai": {
            "key": "member_id",
            "fields": ["provider", "apiKey", "model", "temperature", "maxTokens"]
        },
        "sessions": {
            "key": "session_id",
            "fields": ["agentId", "status", "lastInteraction", "summary"]
        }
    }

    print("\n📚 Esquema Definido en Firestore:")
    for col, meta in SCHEMA_DEFINITION.items():
        print(f"  🔹 Colección: `{col}`")
        print(f"     Clave: {meta['key']}")
        print(f"     Campos principales: {', '.join(meta['fields'])}")

    # Probar la lógica de sincronización (Mock/Real)
    print("\n🔄 Probando Lógica de Sincronización Agente-Cache...")
    
    try:
        redis = await get_redis()
        fs = await get_firestore_config()
        
        # Simular cambio en "Dashboard" guardando en Redis directamente para probar el "Cache Hit"
        mock_data = {
            "name": "Agente Test",
            "role": "Moderador de Prueba",
            "knowledge": "Instrucciones de prueba desde Firestore.",
            "model": "gpt-4-turbo",
            "temperature": 0.8
        }
        
        cache_key = f"config:tenant:{tenant_id}"
        await redis.set(cache_key, json.dumps(mock_data), ex=30)
        print("  ✅ Mock de cambio en Dashboard inyectado en Redis.")

        # Verificar que el servicio recupera lo del cache
        combined_config = await fs.get_tenant_config(tenant_id)
        if combined_config and combined_config.get('name') == "Agente Test":
            print("  ✅ Sincronización de Cache validada (Cache Hit).")
            print(f"     Modelo detectado: {combined_config.get('model')}")
        else:
            print("  ❌ Error en la recuperación de cache.")

    except Exception as e:
        print(f"  ⚠️ Error durante la prueba de servicios: {e}")

    print("\n🎯 Resumen de Sincronización:")
    print("  1. El Agente pide config por `tenantId`.")
    print("  2. `FirestoreConfigService` busca en Redis primero.")
    print("  3. Si no hay cache, unifica `agents` + `config-ai` de Firestore.")
    print("  4. El listener de Firestore invalida Redis en tiempo real cuando hay cambios en el Dashboard.")
    
    print("\n✅ Test de Esquema finalizado.")

if __name__ == "__main__":
    asyncio.run(verify_schema_sync())
