# routes/system_self_repair/execute.py
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

        # 1. No drift → noop
        if not drift.get("drift_detected"):
            return {
                "status": "noop",
                "detail": "No drift detected",
            }

        # 2. Evaluar política
        decision = repair_allowed(drift)

        if not decision["allowed"]:
            return {
                "status": "blocked",
                "detail": decision["reason"],
                "mode": decision["mode"],
            }

        # 3. Permitido, pero todavía no ejecutamos nada (B8.2)
        return {
            "status": "allowed",
            "severity": drift.get("severity"),
            "recommended_action": drift.get("recommended_action"),
            "mode": decision["mode"],
            "note": "Execution deferred (B8.2 decision-only)",
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": f"self-repair execute error: {str(e)}",
        }
