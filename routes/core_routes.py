from fastapi import APIRouter
import requests, os

router = APIRouter(prefix="/core", tags=["Core"])

CORE_URL = os.getenv("NATACHA_CORE_URL", "http://natacha-core:8080")

@router.get("/health")
def core_health():
    try:
        r = requests.get(f"{CORE_URL}/health")
        return {"core_status": "ok", "response": r.json()}
    except Exception as e:
        return {"core_status": "error", "detail": str(e)}
