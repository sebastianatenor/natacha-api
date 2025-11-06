FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY build_stamp.txt /app/.build_stamp
COPY canal_a/ /app/canal_a/
EXPOSE 8080
CMD ["sh","-c","python -m uvicorn canal_a.main:app --host 0.0.0.0 --port ${PORT}"]
