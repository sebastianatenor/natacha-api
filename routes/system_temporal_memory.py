from fastapi import APIRouter
from ops.timeline.reader import read_events

router = APIRouter()

@router.get("/system/memory/temporal/status")
def temporal_memory_status():
    events = read_events()
    return {
        "engine": "temporal_memory",
        "source": "timeline",
        "available": True,
        "event_count": len(events),
        "mode": "rolling",
    }
