from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/system/snapshot/scheduler/status")
def snapshot_scheduler_status():
    return {
        "scheduler": "daily",
        "engine": "snapshot",
        "active": True,
        "started_at": "startup",
        "last_check": datetime.utcnow().isoformat(),
    }
