#!/bin/bash
set -e

# Iniciar Redis Server en segundo plano
echo "Iniciando Redis Server..."
redis-server --daemonize yes

# Esperar a que Redis inicie (con reintentos)
echo "Esperando a Redis..."
for i in {1..5}; do
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis iniciado correctamente."
        break
    fi
    echo "⏳ Esperando Redis ($i/5)..."
    sleep 1
done

# Verificación final
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Error: Redis no respondió al ping."
    # Mostrar logs de redis si es posible (en stdout)
    cat /var/log/redis/redis-server.log || echo "No log defined."
    exit 1
fi

# Iniciar la aplicación FastAPI
echo "Iniciando aplicación..."
exec uvicorn main:server --host 0.0.0.0 --port ${PORT:-8080}
