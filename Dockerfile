# ======================
# Natacha Health Monitor
# ======================

FROM python:3.11-slim

# Instalar utilidades necesarias para ejecutar el script de diagnóstico
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    jq \
    iputils-ping \
    net-tools \
    procps \
 && rm -rf /var/lib/apt/lists/*

# Definir directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código y scripts
COPY . .
COPY check_infra_status.sh /app/check_infra_status.sh
RUN chmod +x /app/check_infra_status.sh

# Variable de entorno
ENV PYTHONUNBUFFERED=1

# Comando principal
CMD ["uvicorn", "health_monitor.app:app", "--host", "0.0.0.0", "--port", "8080"]
