from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/core", tags=["core"])

CORE_URL = "http://localhost:8081"  # Core cognitivo local

@router.get("/ping")
def ping_core():
    """Chequea si el servicio cognitivo está disponible."""
    try:
        r = requests.get(f"{CORE_URL}/health", timeout=3)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
def analyze_text(payload: dict):
    """Envía texto al servicio cognitivo para análisis."""
    try:
        r = requests.post(f"{CORE_URL}/analyze", json=payload, timeout=5)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comunicando con core: {e}")
