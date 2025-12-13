# ===========================
# BASE IMAGE — Python 3.10
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
# Python deps
# ===========================
COPY requirements.txt /app/

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ===========================
# Copy project
# ===========================
COPY . /app

# ===========================
# Env
# ===========================
ENV PYTHONPATH=/app
ENV PORT=8080

# ===========================
# Expose & run
# ===========================
EXPOSE 8080

CMD ["uvicorn", "service_main:app", "--host", "0.0.0.0", "--port", "8080"]
