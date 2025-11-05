from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/ops")

def payload():
    return {
        "ok": True,
        "service": "natacha-api",
        "ts": datetime.utcnow().isoformat() + "Z",
        "checks": {"firestore": "skipped", "env": "skipped"},
    }

@router.get("/smart_health")
def smart_health_get():
    return payload()

@router.post("/smart_health")
def smart_health_post():
    return payload()
