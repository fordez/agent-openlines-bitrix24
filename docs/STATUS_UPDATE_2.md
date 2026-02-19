# Estado del Sistema: 2026-02-19 (Update 2)

## Problema Crítico: Redis Lock Timeout
El bot estaba fallando con `redis.exceptions.LockError: Unable to acquire lock within the time specified` (60s). Esto ocurre porque al limitar la concurrencia (`--concurrency 1`), los mensajes se encolan, y si el procesamiento anterior tarda más de 1 minuto (LLM lento, retry, cold start interno), el siguiente mensaje muere.

## Solución Aplicada
1.  **Extensión de Timeouts**:
    *   `blocking_timeout`: **300s (5 min)** (antes 60s). El mensaje esperará hasta 5 minutos antes de fallar.
    *   `lock_timeout`: **600s (10 min)** (antes 120s). El candado es válido por 10 minutos.

2.  **Manejo de Errores**:
    *   Se envolvió la adquisición del lock en un `try/except LockError`.
    *   Si agota los 5 minutos, responde amigablemente al usuario en lugar de lanzar una excepción 500.

3.  **Limpieza de Código**:
    *   Se corrigió indentación y bloques inalcanzables en `app/agent.py`.

## Recomendación
Desplegar inmediatamente. Esta configuración es **mucho más robusta** para entornos de producción con latencia variable de IA.
