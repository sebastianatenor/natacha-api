# routes/system_self_repair.py
from fastapi import APIRouter

from ops.system.perception_provider import read_system_perception
from ops.cognitive.drift_detector import detect_drift
from ops.cognitive.repair_log import log_repair_proposal

# IMPORTANTE: baseline canónico
from routes.system_baseline.provider import read_system_baseline

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/self-repair")
def self_repair_status():
    baseline = read_system_baseline()
    perception = read_system_perception()

    if not baseline or not perception:
        return {
            "status": "error",
            "detail": "Baseline or perception unavailable",
        }

    drift = detect_drift(baseline, perception)

    if drift.get("drift_detected"):
        log_repair_proposal(drift, baseline)

    return {
        "status": "ok",
        "baseline": baseline,
        "perception": perception,
        "drift": drift,
        "repair_mode": "proposal_only",
    }
