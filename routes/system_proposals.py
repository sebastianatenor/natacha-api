# routes/system_proposals.py
from fastapi import APIRouter
from ops.timeline.reader import read_events

router = APIRouter(tags=["cognitive"])


@router.get("/ops/cognitive/proposals")
def list_proposals(limit: int = 20):
    """
    Read-only cognitive proposals.
    Timeline is the canonical source of truth (B12).
    Filtering is performed at the API layer (B13.1).
    """
    events = read_events()

    proposals = [
        e for e in events
        if e.get("kind") == "cognitive_proposal"
    ]

    return {
        "status": "ok",
        "count": min(len(proposals), limit),
        "proposals": proposals[-limit:]
    }
