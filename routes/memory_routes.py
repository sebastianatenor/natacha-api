from fastapi import APIRouter, HTTPException
import requests
import os

router = APIRouter()

# 🔗 URL base del microservicio de memoria (dentro del entorno Docker)
MEMORY_BASE_URL = os.getenv("MEMORY_BASE_URL", "http://natacha-memory-console:8080")

# Endpoints internos del microservicio de memoria
MEMORY_STORE_URL = f"{MEMORY_BASE_URL}/memory/store"
MEMORY_GET_URL = f"{MEMORY_BASE_URL}/memory/get"
MEMORY_HEALTH_URL = f"{MEMORY_BASE_URL}/health"


@router.get("/memory/health")
def memory_health():
    """Chequea el estado del microservicio de memoria."""
    try:
        res = requests.get(MEMORY_HEALTH_URL, timeout=5)
        return {"memory_status": "ok", "response": res.json()}
    except Exception as e:
        return {"memory_status": "error", "detail": str(e)}


@router.post("/memory/store")
def memory_store(data: dict):
    """
    Guarda un valor en memoria (Firestore + local).
    Envía la solicitud al microservicio `natacha-memory-console`.
    """
    try:
        print(f"🧩 Enviando a {MEMORY_STORE_URL} -> {data}")
        res = requests.post(MEMORY_STORE_URL, json=data, timeout=10)
        print(f"✅ Respuesta memoria: {res.status_code} - {res.text}")

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        return {"memory_status": "ok", "response": res.json()}

    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando con memory-console: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/get/{key}")
def memory_get(key: str):
    """
    Recupera un valor de la memoria remota (Firestore o local).
    """
    try:
        target_url = f"{MEMORY_GET_URL}/{key}"
        print(f"🔍 Solicitando {target_url}")
        res = requests.get(target_url, timeout=10)
        print(f"✅ Respuesta memoria: {res.status_code} - {res.text}")

        if res.status_code != 200:
            raise HTTPException(status_code=res.status_code, detail=res.text)

        return {"memory_status": "ok", "response": res.json()}

    except requests.exceptions.RequestException as e:
        print(f"❌ Error conectando con memory-console: {e}")
        raise HTTPException(status_code=500, detail=str(e))
