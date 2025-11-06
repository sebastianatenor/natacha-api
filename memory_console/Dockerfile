FROM python:3.11-slim
WORKDIR /app

# Evita cache y reduce imagen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY memory_console/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY memory_console/ .

# Cloud Run inyecta PORT. No expongas explícitamente; solo obedecé $PORT.
CMD ["python", "main.py"]
