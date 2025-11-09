FROM python:3.13-slim

WORKDIR /app

# 1) Dependencias básicas (luego podemos mover a requirements.txt)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    google-cloud-firestore \
    google-auth \
    requests

# 2) Copiar código
COPY . /app

# 3) Exponer puerto
EXPOSE 8080

# 4) Ejecutar la app evitando conflicto con el paquete app/
CMD ["uvicorn","service_main:app","--host","0.0.0.0","--port","8080"]
