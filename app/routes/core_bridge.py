from fastapi import APIRouter
import requests
import os

router = APIRouter(prefix="/ops", tags=["core-bridge"])

NATACHA_CORE_URL = os.getenv("NATACHA_CORE_URL", "http://natacha-core:8080")

@router.get("/core-sync")
def core_sync():
    """Sincroniza estado con Natacha Core"""
    try:
        r = requests.get(f"{NATACHA_CORE_URL}/ops/affective-sync", timeout=10)
        if r.status_code == 200:
            return {"status": "ok", "core_response": r.json()}
        else:
            return {"status": "error", "message": f"Core respondió {r.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/core-timeline")
def core_timeline():
    """Obtiene el timeline afectivo desde Natacha Core"""
    try:
        r = requests.get(f"{NATACHA_CORE_URL}/ops/affective-timeline", timeout=10)
        if r.status_code == 200:
            return {"status": "ok", "core_timeline": r.json()}
        else:
            return {"status": "error", "message": f"Core respondió {r.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
