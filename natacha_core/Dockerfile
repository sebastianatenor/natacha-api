# Usa una imagen base liviana de Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de dependencias para aprovechar el caché
COPY requirements.txt .

# Instala todas las dependencias listadas
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente
COPY . .

# Expone el puerto donde corre Uvicorn
EXPOSE 8080

# Comando de inicio del servicio
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
