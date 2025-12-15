FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git gcc g++ libglib2.0-0 libc6 \
    && rm -rf /var/lib/apt/lists/*

# Python deps (runtime)
COPY requirements.runtime.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.runtime.txt

# App
COPY . /app

ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]
