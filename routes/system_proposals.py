# routes/system_proposals.py
from fastapi import APIRouter
from ops.timeline.reader import read_events

router = APIRouter(tags=["cognitive"])


@router.get("/ops/cognitive/proposals")
def list_proposals(limit: int = 20):
    events = read_events(kind="cognitive_proposal")
    return {
        "status": "ok",
        "count": min(len(events), limit),
        "proposals": events[-limit:]
    }
