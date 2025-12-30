from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/system/snapshot/engine/status")
def snapshot_engine_status():
    return {
        "engine": "snapshot",
        "mode": "auto",
        "interval": "daily",
        "running": True,
        "scheduler": "startup",
        "last_heartbeat": datetime.utcnow().isoformat(),
    }
