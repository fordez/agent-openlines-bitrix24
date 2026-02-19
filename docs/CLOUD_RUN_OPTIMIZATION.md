# Optimización de Cloud Run para Cero Fricción

Para que el bot siempre responda instantáneamente y no tenga que "cargar nada" cuando recibe un mensaje, debes configurar Cloud Run con los siguientes parámetros:

## Opción 1: Comando gcloud (Recomendado)
Ejecuta esto en tu terminal para actualizar la configuración:

```bash
gcloud run deploy aibot24-chat \
  --image gcr.io/aibot24-485301/aibot24-chat \
  --min-instances 1 \
  --no-cpu-throttling \
  --memory 1Gi \
  --cpu 2 \
  --region us-central1
```

## Opción 2: Consola de Google Cloud
1. Ve a **Cloud Run** y selecciona tu servicio `aibot24-chat`.
2. Haz clic en **"EDIT & DEPLOY NEW REVISION"**.
3. En la sección **"Capacity"**:
   - Cambia **Min instances** de 0 a **1**.
4. En la sección **"CPU allocation"**:
   - Selecciona **"CPU is always allocated"** (Esto mantiene a Redis y la IA vivos).
5. Haz clic en **Deploy**.

### Beneficios:
*   **Sin Cold Starts:** El primer mensaje de la mañana responderá tan rápido como el último.
*   **Redis Persistente en RAM:** Al no apagarse la instancia, el caché de Redis se mantiene vivo.
*   **IA Caliente:** El servidor MCP estará siempre listo para procesar herramientas.
