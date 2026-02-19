# Análisis de Uso de Redis en AiBot24

Este documento detalla cómo se utiliza Redis en la arquitectura del bot, explicando cada patrón de clave, su propósito y su configuración de tiempo de vida (TTL).

## Resumen General
Redis actúa como la **"Memoria de Trabajo"** rápida del sistema. Su función es doble:
1.  **Velocidad**: Evitar lecturas lentas y costosas a Firestore o API de Bitrix.
2.  **Sincronización**: Coordinar procesos (bloqueos) y compartir estado entre el servidor web (FastAPI) y el servidor de herramientas (MCP).

## Claves y Patrones de Uso

### 1. Control de Concurrencia (Locks)
*   **Clave**: `lock:chat:{chat_id}`
*   **Propósito**: "Semáforo" crítico. Evita que el bot procese dos mensajes del mismo chat simultáneamente. Si llegan dos mensajes, el segundo espera a que el primero termine. Esto previene condiciones de carrera donde el bot podría "olvidar" contexto o responder desordenadamente.
*   **TTL (Tiempo de Vida)**: 10 minutos (timeout máximo) para evitar bloqueos infinitos si el proceso muere.
*   **Ubicación**: `app/sessions.py`

### 2. Historial de Conversación (Context Window)
*   **Clave**: `chat:{chat_id}:history`
*   **Tipo**: Lista (`List`)
*   **Propósito**: Almacena los últimos `N` mensajes (user/assistant) para enviarlos como contexto a la IA en cada turno. Es lo que permite que el bot "recuerde" lo que acabas de decir.
*   **TTL**: 7 días. Si nadie habla en una semana, el bot "olvida" la charla corta para ahorrar RAM.
*   **Ubicación**: `app/memory.py`

### 3. Caché de Configuración (Multi-Tenancy)
*   **Clave**: `config:tenant:{tenant_id}` (donde `tenant_id` es el dominio, ej: `empresa.bitrix24.es`)
*   **Tipo**: String (JSON)
*   **Propósito**: Guarda *toda* la configuración del cliente (Prompt del sistema, Modelo AI, Credenciales, Secretos).
*   **Beneficio**: En lugar de hacer 6 lecturas a Firestore por cada mensaje (lento y costoso), se lee de Redis en <1ms. Se invalida automáticamente si cambias algo en Firestore.
*   **TTL**: 1 hora (o hasta que Firestore notifique un cambio).
*   **Ubicación**: `app/firestore_config.py`

### 4. Gestión de Tokens Bitrix24 (Auth)
*   **Claves**:
    *   `bitrix24:{domain}:access_token`
    *   `bitrix24:{domain}:refresh_token`
    *   `bitrix24:{domain}:expires_at`
*   **Propósito**: Mantiene las credenciales OAuth necesarias para llamar a la API de Bitrix (CRM, Calendario, etc.).
*   **Beneficio**: Comparte los tokens entre el proceso principal y el subproceso MCP. Evita tener que autenticarse en cada petición.
*   **Ubicación**: `app/token_manager.py`

### 5. Mapeo de Contexto
*   **Clave**: `map:chat_to_member:{chat_id}`
*   **Propósito**: Tabla de búsqueda rápida. Dado un ID de chat numérico, nos dice a qué cliente (dominio) pertenece. Es vital para que las herramientas sepan qué CRM consultar.
*   **Ubicación**: `main.py` y `app/token_manager.py`

## Conclusión Técnica
Redis es el componente que permite que el bot sea **scalable** y **rápido**. Sin Redis:
*   Cada mensaje costaría ~6-10 lecturas de Firestore (muy caro).
*   El bot sería ~500ms-1s más lento por respuesta.
*   Habría errores de "doble respuesta" sin los locks.

Es vital monitorear que la memoria de Redis no se llene, aunque con los TTLs actuales el sistema se auto-limpia eficientemente.
