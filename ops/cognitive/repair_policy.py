# ops/cognitive/repair_policy.py
import os

SEVERITY_ORDER = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
}


def repair_allowed(drift: dict) -> dict:
    """
    Decide si un self-repair puede ejecutarse automáticamente.
    Devuelve dict explicativo (auditable).
    """

    armed = os.getenv("SELF_REPAIR_ARMED", "0") == "1"
    max_severity = os.getenv("SELF_REPAIR_MAX_SEVERITY", "medium")

    drift_severity = drift.get("severity", "none")

    if not armed:
        return {
            "allowed": False,
            "reason": "Self-repair not armed",
            "mode": "proposal_only",
        }

    if SEVERITY_ORDER.get(drift_severity, 99) > SEVERITY_ORDER.get(max_severity, 2):
        return {
            "allowed": False,
            "reason": f"Severity '{drift_severity}' exceeds policy",
            "mode": "blocked",
        }

    return {
        "allowed": True,
        "reason": "Policy allows execution",
        "mode": "auto_execute",
    }
