FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir fastapi uvicorn google-cloud-firestore requests
EXPOSE 8080
CMD ["uvicorn", "natacha_app:app", "--host", "0.0.0.0", "--port", "8080"]
