# =========================================
# 🚀 Dockerfile - Natacha Dashboard (Streamlit)
# =========================================
FROM python:3.13-slim

WORKDIR /app

# Instalar dependencias necesarias
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    requests \
    google-cloud-firestore

# Copiar contenido completo del proyecto
COPY . /app

# Configuración para Streamlit
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8080

# Ejecutar el dashboard
CMD ["streamlit", "run", "dashboard/dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
