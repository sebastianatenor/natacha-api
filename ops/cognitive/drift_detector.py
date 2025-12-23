# ops/cognitive/drift_detector.py
from typing import Dict, Any


def detect_drift(baseline: Dict[str, Any], perception: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compara baseline vs percepción REAL.
    Devuelve hechos observables + interpretación semántica.
    """

    drift = {
        "revision_changed": False,
        "semantic_expected": False,
        "semantic_loaded": False,
        "memory_expected": False,
        "memory_exists": False,
        "drift_detected": False,
        "severity": "none",
        "reason": None,
        "recommended_action": None,
    }

    # -------------------------
    # REVISION
    # -------------------------
    if baseline.get("revision") != perception.get("revision"):
        drift["revision_changed"] = True
        drift["drift_detected"] = True
        drift["severity"] = "high"
        drift["reason"] = "Revision mismatch"
        drift["recommended_action"] = "restart_service"
        return drift  # máximo nivel, corto acá

    # -------------------------
    # SEMANTIC
    # -------------------------
    drift["semantic_expected"] = baseline.get("semantic", {}).get("expected_loaded", False)
    drift["semantic_loaded"] = perception.get("semantic", {}).get("loaded", False)

    if drift["semantic_expected"] and not drift["semantic_loaded"]:
        drift["drift_detected"] = True
        drift["severity"] = "medium"
        drift["reason"] = "Semantic core not loaded"
        drift["recommended_action"] = "reload_semantic"
        return drift

    # -------------------------
    # MEMORY
    # -------------------------
    drift["memory_expected"] = baseline.get("memory", {}).get("expected", False)
    drift["memory_exists"] = perception.get("memory", {}).get("exists", False)

    if drift["memory_expected"] and not drift["memory_exists"]:
        drift["drift_detected"] = True
        drift["severity"] = "high"
        drift["reason"] = "Memory expected but missing"
        drift["recommended_action"] = "restore_memory"
        return drift

    # -------------------------
    # NO DRIFT
    # -------------------------
    return drift
