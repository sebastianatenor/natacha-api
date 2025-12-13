from typing import Dict, Any


def interpret_system_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpreta el estado del sistema de forma consistente con lazy memory.
    """

    semantic = state.get("semantic", {})
    memory = state.get("memory", {})
    runtime = state.get("runtime", {})

    semantic_loaded = bool(semantic.get("loaded"))
    memory_loaded = bool(memory.get("store_loaded"))
    memory_available = bool(memory.get("store_available"))

    # 🧠 NUEVA lógica correcta
    memory_present = memory_loaded or memory_available

    warnings = []

    if not semantic_loaded:
        warnings.append("Semantic core not loaded")

    if not memory_present:
        warnings.append("Memory store not present")

    status = "optimal" if not warnings else "degraded"

    return {
        "status": status,
        "issues": [],
        "warnings": warnings,
        "summary": {
            "semantic_loaded": semantic_loaded,
            "memory_present": memory_present,
            "cloud_run": bool(runtime.get("cloud_run")),
        }
    }
