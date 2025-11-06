# Imagen base oficial de Python
FROM python:3.10-slim

# Setear directorio de trabajo
WORKDIR /app

# Copiar requirements y dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# Entrypoint principal
ENV APP_MODULE=main:app

# Exponer puerto
EXPOSE 8080

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
