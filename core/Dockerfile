FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn google-cloud-firestore google-auth requests
EXPOSE 8080
CMD ["uvicorn", "natacha_app:app", "--host", "0.0.0.0", "--port", "8080"]
