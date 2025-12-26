from fastapi import APIRouter
from ops.system.perception_provider import read_system_perception
from ops.system.full_status_provider import read_full_status
from ops.cognitive.signals.engine import collect_signals

router = APIRouter(tags=["cognitive"])

@router.get("/ops/cognitive/signals")
def list_signals():
    perception = read_system_perception()
    status = read_full_status()
    signals = collect_signals(perception, status)
    return {
        "status": "ok",
        "count": len(signals),
        "signals": [s.model_dump() for s in signals]
    }
