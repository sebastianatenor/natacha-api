"""
System Interpreter
Lee system_state y devuelve diagnóstico interpretado.
NO inicializa servicios.
NO escribe estado.
"""
from typing import Dict, Any

def interpret_system_state(state: Dict[str, Any]) -> Dict[str, Any]:
    issues = []
    warnings = []

    # Semantic
    if not state.get("semantic", {}).get("loaded"):
        warnings.append("Semantic core not loaded")

    # Memory
    if not state.get("memory", {}).get("store_present"):
        warnings.append("Memory store not present")

    # Infra
    if state.get("infra", {}).get("health_routes") != "loaded":
        issues.append("Health routes missing")

    status = "ok"
    if issues:
        status = "error"
    elif warnings:
        status = "degraded"

    return {
        "status": status,
        "issues": issues,
        "warnings": warnings,
        "summary": {
            "semantic_loaded": state.get("semantic", {}).get("loaded"),
            "memory_present": state.get("memory", {}).get("store_present"),
            "cloud_run": state.get("runtime", {}).get("cloud_run"),
        }
    }
