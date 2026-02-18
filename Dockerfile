FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# No se instala gcc para evitar esperas largas en apt-get si no es estrictamente necesario
# Instalar Redis y dependencias básicas
RUN apt-get update && apt-get install -y --no-install-recommends \
    redis-server \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

# Dar permisos de ejecución al script de inicio
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]
