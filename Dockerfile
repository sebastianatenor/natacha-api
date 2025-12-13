# ===========================
# BASE IMAGE — Python 3.10 LTS (compatible con transformers, torch y embeddings)
# ===========================
FROM python:3.10-slim

# ===========================
# System deps
# ===========================
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    libglib2.0-0 \
    libc6 \
    && rm -rf /var/lib/apt/lists/*

# ===========================
# Workdir
# ===========================
WORKDIR /app

# ===========================
# Python libs (primer pase)
# ===========================
COPY requirements.txt /app/

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer model at build time
RUN python - <<EOF
from sentence_transformers import SentenceTransformer
SentenceTransformer("all-MiniLM-L6-v2")
print("Model cached successfully")
EOF

# ===========================
# Copiar todo el proyecto
# ===========================
COPY . /app

# ===========================
# Variables de entorno
# ===========================
ENV PYTHONPATH=/app
ENV PORT=8080

# ===========================
# Expose & run
# ===========================
EXPOSE 8080

CMD ["sh", "-c", "scripts/bootstrap_memory.sh && uvicorn service_main:app --host 0.0.0.0 --port 8080"]
