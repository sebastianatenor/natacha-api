# ==========================================
# Natacha Core – Cloud Run build (v18.6)
# ==========================================

FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del core
COPY . .

# Asegurar que el módulo se encuentre
ENV PYTHONPATH="/app"

# Puerto para Cloud Run
EXPOSE 8080

# Comando de arranque CORRECTO
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
