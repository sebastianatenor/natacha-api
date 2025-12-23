from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.post("/self-repair/execute")
def execute_self_repair():
    try:
        from routes.system_baseline.provider import read_system_baseline
        from ops.system.perception_provider import read_system_perception
        from ops.cognitive.drift_detector import detect_drift
        from ops.cognitive.repair_policy import repair_allowed

        baseline = read_system_baseline()
        perception = read_system_perception()
        drift = detect_drift(baseline, perception)

        decision = repair_allowed(drift)

        if not drift.get("drift_detected"):
            return {
                "status": "noop",
                "detail": "No drift detected",
            }

        if not decision["allowed"]:
            return {
                "status": "blocked",
                "detail": decision["reason"],
                "mode": decision["mode"],
            }

        # ⛔ Todavía NO ejecutamos nada
        return {
            "status": "allowed",
            "severity": drift.get("severity"),
            "action": drift.get("recommended_action"),
            "mode": decision["mode"],
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": f"self-repair execute failed: {str(e)}",
        }
