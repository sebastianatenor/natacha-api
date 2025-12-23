from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/self-repair")
def self_repair_status():
    try:
        from ops.system.perception_provider import read_system_perception
        from routes.system_baseline.provider import read_system_baseline
        from ops.cognitive.drift_detector import detect_drift
        from ops.cognitive.repair_log import log_repair_proposal

        baseline = read_system_baseline()
        perception = read_system_perception()

        if not baseline or not perception:
            return {
                "status": "error",
                "detail": "Baseline or perception unavailable",
                "repair_mode": "proposal_only",
            }

        drift = detect_drift(baseline, perception)

        if drift.get("drift_detected"):
            try:
                log_repair_proposal(drift, baseline)
            except Exception as e:
                return {
                    "status": "warning",
                    "detail": f"Drift detected but logging failed: {e}",
                    "repair_mode": "proposal_only",
                }

        return {
            "status": "ok",
            "drift_detected": drift.get("drift_detected", False),
            "repair_mode": "proposal_only",
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": f"self-repair internal error: {e}",
            "repair_mode": "proposal_only",
        }
