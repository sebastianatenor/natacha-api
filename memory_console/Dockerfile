FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn google-cloud-firestore
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
