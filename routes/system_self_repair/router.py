# routes/system_self_repair/router.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.post("/self-repair/execute")
def self_repair_execute():
    """
    B12.2 — Executes safe autonomous self-repair actions
    """
    try:
        from routes.system_baseline.provider import read_system_baseline
        from ops.system.perception_provider import read_system_perception
        from ops.cognitive.drift_detector import detect_drift
        from ops.cognitive.repair_executor import execute_repair

        baseline = read_system_baseline()
        perception = read_system_perception()

        drift = detect_drift(baseline, perception)

        if not drift.get("drift_detected"):
            return {
                "status": "noop",
                "detail": "No drift detected",
            }

        return execute_repair(drift)

    except Exception as e:
        return {
            "status": "error",
            "detail": f"self-repair execute error: {str(e)}",
        }


@router.post("/self-repair/execute")
def self_repair_execute():
    """
    Ejecuta autoreparación SOLO si:
    - Hay drift
    - SELF_REPAIR_ARMED=1
    """
    try:
        if os.getenv("SELF_REPAIR_ARMED") != "1":
            return {
                "status": "blocked",
                "detail": "Self-repair not armed",
                "mode": "proposal_only",
            }

        from routes.system_baseline.provider import read_system_baseline
        from ops.system.perception_provider import read_system_perception
        from ops.cognitive.drift_detector import detect_drift
        from ops.cognitive.repair_policy import repair_allowed

        baseline = read_system_baseline()
        perception = read_system_perception()
        drift = detect_drift(baseline, perception)

        if not drift.get("drift_detected"):
            return {
                "status": "noop",
                "detail": "No drift detected",
            }

        decision = repair_allowed(drift)

        if not decision["allowed"]:
            return {
                "status": "blocked",
                "detail": decision["reason"],
                "mode": decision["mode"],
            }

        return {
            "status": "allowed",
            "severity": drift.get("severity"),
            "recommended_action": drift.get("recommended_action"),
            "mode": decision["mode"],
            "note": "Execution deferred (B8.2 decision-only)",
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "detail": f"self-repair execute error: {str(e)}",
            },
        )
