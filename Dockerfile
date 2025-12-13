FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git gcc g++ libglib2.0-0 libc6 \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# App
COPY . /app
ENV PYTHONPATH=/app
ENV PORT=8080

EXPOSE 8080

# ✅ Cloud Run SAFE
CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]
