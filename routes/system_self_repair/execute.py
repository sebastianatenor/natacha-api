from fastapi import APIRouter, HTTPException

from ops.system.perception_provider import read_system_perception
from routes.system_baseline.provider import read_system_baseline
from ops.cognitive.drift_detector import detect_drift
from ops.cognitive.repair_executor import execute_repair

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.post("/self-repair/execute")
def execute_self_repair():
    baseline = read_system_baseline()
    perception = read_system_perception()

    if not baseline or not perception:
        raise HTTPException(
            status_code=503,
            detail="Baseline or perception unavailable",
        )

    drift = detect_drift(baseline, perception)

    if not drift.get("drift_detected"):
        return {
            "status": "noop",
            "detail": "No drift detected",
        }

    result = execute_repair(drift, baseline)
    return result
