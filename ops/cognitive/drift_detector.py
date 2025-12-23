# ops/cognitive/drift_detector.py
from typing import Dict, Any


def detect_drift(baseline: Dict[str, Any], perception: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compara baseline vs percepción REAL.
    Devuelve solo hechos observables.
    """

    drift = {
        "revision_changed": False,
        "semantic_expected": False,
        "semantic_loaded": False,
        "memory_expected": False,
        "memory_exists": False,
        "drift_detected": False,
    }

    # Revision
    if baseline.get("revision") != perception.get("revision"):
        drift["revision_changed"] = True

    # Semantic
    drift["semantic_expected"] = baseline.get("semantic", {}).get("expected_loaded", False)
    drift["semantic_loaded"] = perception.get("semantic", {}).get("loaded", False)

    # Memory
    drift["memory_expected"] = baseline.get("memory", {}).get("expected", False)
    drift["memory_exists"] = perception.get("memory", {}).get("exists", False)

    drift["drift_detected"] = any([
        drift["revision_changed"],
        drift["semantic_expected"] and not drift["semantic_loaded"],
        drift["memory_expected"] and not drift["memory_exists"],
    ])

    return drift
