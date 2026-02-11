FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# No se instala gcc para evitar esperas largas en apt-get si no es estrictamente necesario
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código del proyecto
COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:server", "--host", "0.0.0.0", "--port", "8080"]
