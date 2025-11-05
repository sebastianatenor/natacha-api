FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY build_stamp.txt /app/.build_stamp
COPY . /app

EXPOSE 8080

# ⚠️ Usar ${PORT} que entrega Cloud Run (no hardcodear 8080)
CMD ["sh","-c","python -m uvicorn app_shim:app --host 0.0.0.0 --port ${PORT}"]
