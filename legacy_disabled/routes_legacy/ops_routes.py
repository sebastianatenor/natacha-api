from fastapi import APIRouter
from datetime import datetime
router = APIRouter(prefix="/ops")
@router.get("/smart_health")
def smart_health_get():
    return {"ok": True, "service": "natacha-api", "ts": datetime.utcnow().isoformat()+"Z",
            "checks": {"firestore": "skipped", "env": "skipped"}}
