FROM python:3.13-slim

WORKDIR /app

# 1. instalar dependencias
# si querés, después lo pasamos a requirements.txt
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    google-cloud-firestore \
    google-auth \
    requests

# 2. copiar TODO el proyecto (no solo app.py)
COPY . /app
# deps
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check || true

# 3. exponer puerto
EXPOSE 8080

# 4. levantar la misma app que levantás en tu Mac
CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]ENV PYTHONPATH=/app

# harden: ensure gcs lib present (also breaks cache)
RUN pip install --no-cache-dir google-cloud-storage==2.16.0
