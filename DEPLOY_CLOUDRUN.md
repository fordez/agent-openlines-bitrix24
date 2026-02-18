# Despliegue en Google Cloud Run con Redis Embebido

Este servicio se despliega en Cloud Run utilizando un contenedor que incluye tanto la aplicación FastAPI como una instancia local de Redis.

## Configuración de Recursos
- **CPU**: 2 vCPU
- **Memoria**: 1Gi (Ajustable según necesidad, "media ram" interpretado como 1GB para balancear con 2 vCPUs)
- **Puerto**: 8080

## Comandos de Despliegue

### 1. Construir y Desplegar directamente (desde código fuente)

```bash
gcloud run deploy aibot24-chat \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --cpu 2 \
  --set-env-vars=REDIS_URL=redis://localhost:6379/0
```

### 2. Variables de Entorno
Asegúrate de configurar las variables de entorno necesarias (claves API, etc.) en Cloud Run o pasarlas con `--set-env-vars`.

Para ver la lista completa de variables requeridas (como `FIRESTORE_PROJECT_ID`), consulta la guía principal: [SETUP_CICD.md](./SETUP_CICD.md).

> **Nota**: La configuración del Agente (Role, Prompt) y **API Keys de LLM** se cargan dinámicamente desde Firestore (`config-ai`), no via variables de entorno.

## Notas
- Redis corre en el mismo contenedor, por lo que los datos **NO son persistentes** entre reinicios (Cloud Run es stateless). Si necesitas persistencia a largo plazo, usa Redis Enterprise o Cloud Memorystore. Para caché temporal, esta solución es ideal.
