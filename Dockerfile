FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    google-cloud-firestore \
    google-auth \
    requests

COPY . /app

EXPOSE 8080

CMD ["uvicorn","service_main:app","--host","0.0.0.0","--port","8080"]
