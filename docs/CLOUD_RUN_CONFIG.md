# Configuración de Cloud Run (Actualizada: 2026-02-19)

Se ha aplicado la siguiente configuración de escalado al servicio `aibot24-chat`:

*   **Región**: `us-central1`
*   **Instancias Mínimas**: `1` (Evita Cold Starts)
*   **Concurrencia**: `1` (Procesamiento exclusivo por request)

## Comando ejecutado
```bash
gcloud run services update aibot24-chat --min-instances 1 --concurrency 1 --region us-central1
```

## Implicaciones
1.  **Costo**: Se facturará por 1 instancia activa 24/7.
2.  **Rendimiento**: La latencia inicial desaparece. Si llegan múltiples mensajes simultáneos, Cloud Run escalará horizontalmente (más instancias) en lugar de verticalmente (más hilos), lo cual es más seguro pero ligeramente más lento en escalar si el tráfico sube de golpe.
