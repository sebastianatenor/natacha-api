# routes/system_proposals.py
from fastapi import APIRouter
from ops.timeline.reader import read_events

router = APIRouter(prefix="/ops/cognitive", tags=["cognitive"])


@router.get("/proposals")
def list_proposals(limit: int = 20):
    events = read_events()

    proposals = [
        e for e in events
        if e.get("kind") == "cognitive_proposal"
    ]

    lifecycle = {}
    for e in events:
        if e.get("kind") == "cognitive_proposal_lifecycle":
            d = e.get("details", {})
            lifecycle[d["proposal_id"]] = d["new_state"]

    enriched = []
    for p in proposals[-limit:]:
        p["proposal_id"] = p.get("event_id")
        d = p.get("details", {})
        pid = p["proposal_id"]
        d["lifecycle_state"] = lifecycle.get(pid, "proposed")
        enriched.append(p)

    return {
        "status": "ok",
        "count": len(enriched),
        "proposals": enriched,
    }
