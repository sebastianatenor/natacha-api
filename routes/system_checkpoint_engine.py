from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/system/checkpoint/engine/status")
def checkpoint_engine_status():
    return {
        "engine": "checkpoint",
        "mode": "manual+auto",
        "running": True,
        "restorable": True,
        "last_check": datetime.utcnow().isoformat(),
    }
