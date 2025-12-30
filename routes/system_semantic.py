from fastapi import APIRouter
from ops.timeline.writer import write_event

router = APIRouter()

@router.post("/system/semantic/bootstrap")
def semantic_bootstrap(
    engine: str = "v17",
    mode: str = "shadow",
    semantic_mode: str = "heuristic_only"
):
    event = write_event(
        kind="semantic_state",
        subsystem="semantic",
        state="registered",
        revision=engine,
        confidence=1.0,
        details={
            "engine": engine,
            "mode": mode,
            "semantic_mode": semantic_mode,
            "vector": "declared_only"
        },
    )

    return {
        "status": "ok",
        "semantic_engine": "registered",
        "semantic_mode": semantic_mode,
        "event_id": event["event_id"],
    }

def semantic_status():
    return {
        "engine": "v17",
        "mode": "shadow",
        "semantic_mode": "heuristic_only",
        "vector": "declared_only",
        "initialized": True
    }
