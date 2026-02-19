# Flujo de Datos desde Firestore

El bot construye su "cerebro" y configuración combinando datos de **6 colecciones diferentes** de Firestore en cada arranque de sesión. Aquí está el desglose exacto de qué trae de dónde:

## 1. Identidad y Acceso (`installations/{dominio}`)
*   **Qué trae**: Tokens de acceso a Bitrix24.
*   **Campos**: `accessToken`, `refreshToken`, `expiresAt`, `domain`.
*   **Para qué sirve**: Para que el bot pueda leer/escribir en tu CRM sin pedir login.

## 2. Secretos de la App (`config-secrets/{dominio}`)
*   **Qué trae**: Credenciales de la aplicación Bitrix (Client ID/Secret).
*   **Campos**: `clientId`, `clientSecret`.
*   **Para qué sirve**: Para renovar los tokens anteriores cuando caducan.
*   **Nota**: Estos son críticos y tienen prioridad máxima.

## 3. Configuración del Agente Activo (`agents` - Query)
*   **Qué trae**: La personalidad y cerebro del bot. Busca el agente donde `tenantId == dominio` y `isActive == true`.
*   **Campos**:
    *   `role`: El rol del bot (ej. "Asistente de Viajes").
    *   `systemPrompt`: Las instrucciones maestras de cómo comportarse.
    *   `model`: El modelo de IA (ej. `gpt-4`).
    *   `temperature`: Creatividad (0.0 a 1.0).
    *   `provider`: `openai` o `google`.
    *   `openaiApiKey` / `googleApiKey`: **Tus claves de API (¡Importante!)**.
*   **Para qué sirve**: Define *quién* es el bot y *cómo* piensa.

## 4. Configuración Global AI (`settings/ai`)
*   **Qué trae**: Valores por defecto para la IA si el agente no tiene específicos.
*   **Para qué sirve**: Fallback de seguridad.

## 5. Arquitectura y Personalidad (`config-architect/{dominio}`)
*   **Qué trae**: Ajustes de alto nivel definidos por el "Arquitecto" (tu herramienta de configuración).
*   **Para qué sirve**: Personalización base del tenant.

## 6. Configuración de App/UI (`config-app/{dominio}`)
*   **Qué trae**: Configuraciones generales de la aplicación web.
*   **Para qué sirve**: Ajustes de interfaz o comportamiento general.

---

## Cómo se Combina (Prioridad)
El bot mezcla todos estos datos en un solo objeto de configuración. Si hay conflictos (ej. el modelo está definido en `settings/ai` Y en `agents`), gana el más específico según este orden (de mayor a menor prioridad):

1.  **Secretos** (`config-secrets`) 🏆 *Gana siempre*
2.  **Agente Activo** (`agents`) 🥈 *Define el comportamiento*
3.  **Global AI** (`settings/ai`)
4.  **Arquitectura** (`config-architect`)
5.  **App App** (`config-app`)

De esta forma, la configuración de tu **Agente Activo** siempre sobrescribe a las configuraciones globales, dándote control total por cliente.
