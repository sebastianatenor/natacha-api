k# routes/system_self_repair/router.py
from fastapi import APIRouter
from fastapi.responses import JSONResponse
import os

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/self-repair")
def self_repair_status():
    try:
        from routes.system_baseline.provider import read_system_baseline
        from ops.system.perception_provider import read_system_perception
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
            log_repair_proposal(drift, baseline)

        return {
            "status": "ok",
            "baseline": baseline,
            "perception": perception,
            "drift": drift,
            "repair_mode": "proposal_only",
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": f"self-repair internal error: {str(e)}",
            "repair_mode": "proposal_only",
        }


@router.post("/self-repair/execute")
def self_repair_execute():
    """
    B8.2: solo DECIDE, no ejecuta.
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

        if not baseline or not perception:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "detail": "Baseline or perception unavailable",
                },
            )

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
