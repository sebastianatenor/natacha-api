from fastapi import APIRouter
from ops.timeline.reader import read_timeline
from ops.symbolic.narrative import derive_state_from_events

router = APIRouter(prefix="/ops/system", tags=["System"])

@router.get("/memory_diagnostic")
def memory_diagnostic():
    events = read_timeline(limit=500)
    derived = derive_state_from_events(events)

    return {
        "memory_engine": "timeline+ndjson",
        "semantic_loaded": derived["semantic_loaded"],
        "snapshots": derived["snapshot_count"],
        "checkpoints": derived["checkpoint_count"],
        "maturity": derived["maturity"],
        "confidence": "high"
    }
