# Reporte de Testing: Esquema Firestore y Sincronización

Este documento resume la verificación del esquema de datos y la funcionalidad de sincronización entre el Dashboard (Firestore) y el motor de Chat (Redis/Agente).

## 1. Verificación del Esquema (Firestore)

Tras analizar los archivos de definición y scripts de inicialización, se ha validado el siguiente esquema:

| Colección | Clave (Doc ID) | Campos Clave | Propósito |
|-----------|----------------|--------------|-----------|
| `agents` | `auto-id` | `tenantId`, `role`, `objective`, `tone`, `knowledge`, `model` | Configuración específica del agente. |
| `config-ai` | `member_id` | `model`, `temperature`, `apiKey`, `maxTokens` | Configuración base de IA por portal. |
| `installations`| `member_id` | `domain`, `accessToken`, `status`, `expiresAt` | Datos de enlace con Bitrix24. |
| `sessions` | `session_id` | `agentId`, `status`, `lastInteraction`, `summary` | Persistencia de estados de chat. |

## 2. Lógica de Sincronización de Agentes

El sistema de sincronización implementado en `aibot24-chat` garantiza que el agente siempre use la última configuración definida en el Dashboard:

1. **Unificación de Datos**: El servicio `FirestoreConfigService` combina los parámetros de `config-ai` (base) con los de `agents` (específicos del rol).
2. **Inyección en Prompt**: El bot ahora construye su personalidad dinámicamente:
   - *Prompt*: `Eres {role}. Tu objetivo es: {objective}. Tu tono debe ser {tone}. {knowledge}`.
3. **Caché Distribuido (Redis)**: Se usa Redis para evitar latencia en cada mensaje.
4. **Invalidación en Tiempo Real**: Un listener escucha cambios en Firestore e invalida el caché de Redis inmediatamente, forzando al bot a usar la nueva configuración en la siguiente interacción.

## 3. Pruebas Realizadas

- **Script de Verificación**: Se creó `testing/verify_schema_sync.py` para validar la lógica de recuperación y cache.
- **Validación de Limpieza**: Se confirmó que Redis se limpia al iniciar/finalizar sesiones para evitar colisiones de datos.
- **Consistencia de Tipos**: Se alinearon los campos de Python con los tipos definidos en TypeScript (`AIAgent`, `AIConfig`).

---
*Nota: Para ejecución en producción, el sistema requiere el archivo `firestore-key.json` configurado en el `.env`.*
