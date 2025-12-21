from fastapi import APIRouter

from ops.timeline.reader import read_events, get_derived_state

router = APIRouter(prefix="/ops/system", tags=["System"])

@router.get("/memory_diagnostic")
def memory_diagnostic():
    events = read_events()
    derived = get_derived_state()

    return {
        "status": "ok",
        "engine": "timeline-reader",
        "events_count": len(events),
        "semantic_loaded": derived["semantic_loaded"],
        "snapshots": derived["snapshot_count"],
        "checkpoints": derived["checkpoint_count"],
        "maturity": derived["maturity"],
        "confidence": "high",
    }
