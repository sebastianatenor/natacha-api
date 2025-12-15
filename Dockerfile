FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git gcc g++ libglib2.0-0 libc6 \
    && rm -rf /var/lib/apt/lists/*

# Runtime deps mínimas
RUN pip install --no-cache-dir \
    fastapi==0.115.3 \
    "uvicorn[standard]==0.30.6"

# App
COPY . /app

ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]
