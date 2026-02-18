#!/bin/bash
set -e

# Iniciar Redis Server en segundo plano
echo "Iniciando Redis Server..."
redis-server --daemonize yes

# Esperar a que Redis inicie (opcional, pero recomendado)
sleep 1

# Verificar si Redis está corriendo
if pgrep "redis-server" > /dev/null; then
    echo "Redis iniciado correctamente."
else
    echo "Error al iniciar Redis."
    exit 1
fi

# Iniciar la aplicación FastAPI
echo "Iniciando aplicación..."
exec uvicorn main:server --host 0.0.0.0 --port ${PORT:-8080}
