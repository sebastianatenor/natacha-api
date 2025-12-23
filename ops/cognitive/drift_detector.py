# ops/cognitive/drift_detector.py
from typing import Dict, Any


def detect_drift(baseline: Dict[str, Any], perception: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compara baseline vs percepción REAL.
    Devuelve hechos observables + severidad cognitiva.

    severity:
      - none   → sistema alineado
      - soft   → desviación tolerable
      - hard   → requiere reparación automática
      - fatal  → sistema inconsistente (bloqueo)
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
    }

    # -------------------------------------------------
    # REVISION
    # -------------------------------------------------
    if baseline.get("revision") != perception.get("revision"):
        drift["revision_changed"] = True

    # -------------------------------------------------
    # SEMANTIC
    # -------------------------------------------------
    drift["semantic_expected"] = baseline.get("semantic", {}).get("expected_loaded", False)
    drift["semantic_loaded"] = perception.get("semantic", {}).get("loaded", False)

    # -------------------------------------------------
    # MEMORY
    # -------------------------------------------------
    drift["memory_expected"] = baseline.get("memory", {}).get("expected", False)
    drift["memory_exists"] = perception.get("memory", {}).get("exists", False)

    # -------------------------------------------------
    # DRIFT DETECTION
    # -------------------------------------------------
    drift["drift_detected"] = any([
        drift["revision_changed"],
        drift["semantic_expected"] and not drift["semantic_loaded"],
        drift["memory_expected"] and not drift["memory_exists"],
    ])

    # -------------------------------------------------
    # SEVERITY CLASSIFICATION (B8)
    # -------------------------------------------------
    if not drift["drift_detected"]:
        drift["severity"] = "none"
        drift["reason"] = None
        return drift

    # Fatal: revision mismatch (estado no confiable)
    if drift["revision_changed"]:
        drift["severity"] = "fatal"
        drift["reason"] = "revision_mismatch"
        return drift

    # Hard: memoria esperada pero ausente (recuperable)
    if drift["memory_expected"] and not drift["memory_exists"]:
        drift["severity"] = "hard"
        drift["reason"] = "memory_missing"
        return drift

    # Soft: semántica no cargada pero no requerida
    if drift["semantic_expected"] and not drift["semantic_loaded"]:
        drift["severity"] = "soft"
        drift["reason"] = "semantic_not_loaded"
        return drift

    # Fallback (no debería ocurrir)
    drift["severity"] = "soft"
    drift["reason"] = "unspecified_drift"
    return drift
