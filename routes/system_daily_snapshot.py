# routes/system_daily_snapshot.py
from fastapi import APIRouter
from datetime import datetime

from ops.timeline.writer import write_event

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.post("/daily_snapshot")
def daily_snapshot():
    """
    B11 canonical daily snapshot.
    Writes an immutable snapshot event into the timeline.
    """

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "daily_snapshot",
        "confidence": "high",
    }

    write_event(event)

    return {
        "status": "ok",
        "snapshot": "daily",
        "timestamp": event["timestamp"],
    }
