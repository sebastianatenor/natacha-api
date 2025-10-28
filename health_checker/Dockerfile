FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Instalamos dependencias necesarias
RUN pip install --no-cache-dir google-cloud-firestore requests

# Aseguramos que Python vea los módulos base
ENV PYTHONPATH="/app"
ENV LOG_DIR="/app/logs"
RUN mkdir -p /app/logs

# Ejecuta el monitor en bucle infinito
CMD ["python3", "/app/health_monitor.py"]
