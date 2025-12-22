from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter(
    prefix="/ops/system",
    tags=["system"],
)

@router.get("/perception")
def system_perception():
    """
    Percepción REAL del estado del agente.
    No razona. No infiere. Lee únicamente el último snapshot registrado.
    """

    try:
        from ops.timeline.reader import read_events
        events = read_events()
    except Exception as e:
        return {
            "status": "error",
            "error": f"timeline_unavailable: {e}"
        }

    # Buscar último daily_snapshot
    snapshots = [e for e in events if e.get("kind") == "daily_snapshot"]

    if not snapshots:
        return {
            "status": "ok",
            "perception": None,
            "confidence": "low",
            "note": "no daily_snapshot found"
        }

    last = snapshots[-1]

    try:
        ts = datetime.fromisoformat(last["timestamp"])
        age_seconds = int((datetime.now(timezone.utc) - ts).total_seconds())
    except Exception:
        age_seconds = None

    return {
        "status": "ok",
        "perception": {
            "snapshot": last,
            "age_seconds": age_seconds,
        },
        "confidence": "high"
    }
