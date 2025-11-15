"""
🧩 Extensión temporal para enlazar la API principal con el Core Cognitivo local.
Ruta: /ops/core/analyze
"""

from fastapi import APIRouter, HTTPException
import requests

router = APIRouter(prefix="/ops/core", tags=["ops-core"])

CORE_URL = "http://natacha-core:8080"

@router.get("/ping")
def ping_core():
    """Verifica si el Core Cognitivo local responde."""
    try:
        r = requests.get(f"{CORE_URL}/health", timeout=3)
        return {"status": "ok", "core_response": r.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo contactar al core: {e}")

@router.post("/analyze")
def analyze_with_core(payload: dict):
    """Envía un texto al Core Cognitivo para análisis y devuelve la respuesta."""
    try:
        r = requests.post(f"{CORE_URL}/analyze", json=payload, timeout=5)
        return r.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comunicando con el core: {e}")
