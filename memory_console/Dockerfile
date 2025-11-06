FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copiamos SOLO lo necesario para la build del servicio
COPY memory_console/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del servicio
COPY memory_console/ .

# Exponé el puerto "estándar" para documentación (Cloud Run pasa $PORT)
EXPOSE 8080

# Ejecuta uvicorn apuntando a main:app y tomando el puerto de $PORT
CMD ["bash", "-lc", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
