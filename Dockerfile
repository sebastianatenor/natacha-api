FROM python:3.13-slim

WORKDIR /app

# --- cache-buster / runtime marker ---
ARG REV=dev
ENV RUNTIME_REV=$REV
ENV PYTHONPATH=/app

# 1. deps base para levantar rápido (antes de copiar el repo)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    google-cloud-firestore \
    google-auth \
    requests \
    google-cloud-storage==2.16.0

# 2. copiar TODO el proyecto
COPY . /app
RUN ls -la /app/routes || true
RUN python -c 'import importlib,sys; print("[BUILD] trying import routes.memory_v2"); m=importlib.import_module("routes.memory_v2"); rp=getattr(getattr(m,"router",None),"prefix",None); print("[BUILD] memory_v2 import OK; prefix=", rp)'
# registrar revisión para invalidar caché de capas
RUN echo "$RUNTIME_REV" > /app/.rev

# 3. si hay requirements.txt, instalarlos (idempotente)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && ( [ -f requirements.txt ] && pip install --no-cache-dir -r requirements.txt || true ) \
    && pip check || true

# 4. puerto
EXPOSE 8080

# 5. comando
CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]
