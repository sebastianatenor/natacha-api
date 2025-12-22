from fastapi import APIRouter
from ops.timeline.reader import read_events

router = APIRouter(tags=["memory"])

@router.get("/memory/recent")
def memory_recent(limit: int = 20):
    events = read_events()
    return {
        "status": "ok",
        "count": min(len(events), limit),
        "events": events[-limit:]
    }
