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
  --set-env-vars=REDIS_URL=redis://localhost:6379/0,OPENAI_API_KEY=sk-xxx,AI_MODEL=gpt-4o,AI_TEMPERATURE=0.7
```

### 2. Variables de Entorno Requeridas
| Variable | Descripción |
| --- | --- |
| `REDIS_URL` | `redis://localhost:6379/0` (Para el redis embebido) |
| `OPENAI_API_KEY` | Tu llave maestra para todos los clientes |
| `AI_MODEL` | El modelo por defecto (ej: `gpt-4o`) |
| `AI_TEMPERATURE` | Nivel de creatividad (ej: `0.7`) |
| `FIRESTORE_KEY_CONTENT` | (Base64) Para autenticación con Firestore |

> **Nota**: El **System Prompt** (personalidad) se sigue cargando dinámicamente desde Firestore para permitir personalización por cliente, pero la maquinaria de OpenAI ahora es global.

## Notas
- Redis corre en el mismo contenedor, por lo que los datos **NO son persistentes** entre reinicios (Cloud Run es stateless). Si necesitas persistencia a largo plazo, usa Redis Enterprise o Cloud Memorystore. Para caché temporal, esta solución es ideal.
