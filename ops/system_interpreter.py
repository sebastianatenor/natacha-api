from typing import Dict, Any


def interpret_system_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpreta el estado crudo del sistema y devuelve una evaluación semántica.
    NO ejecuta acciones. SOLO razona.
    """

    interpretation = {
        "overall": "unknown",
        "signals": [],
        "warnings": [],
        "notes": []
    }

    # -------------------------
    # Semantic core
    # -------------------------
    semantic = state.get("semantic", {})
    if not semantic.get("loaded"):
        interpretation["signals"].append("semantic_cold")
        interpretation["notes"].append(
            "Semantic core not loaded yet (expected if no warmup)."
        )

    if not semantic.get("hf_token_present"):
        interpretation["warnings"].append(
            "HF_TOKEN not present; HuggingFace rate limits may apply."
        )

    # -------------------------
    # Memory
    # -------------------------
    memory = state.get("memory", {})
    if not memory.get("store_present"):
        interpretation["warnings"].append(
            "Memory store file not present in runtime."
        )

    # -------------------------
    # Introspection
    # -------------------------
    intro = state.get("introspection", {})
    if intro.get("history") == "loaded":
        interpretation["signals"].append("introspection_available")

    # -------------------------
    # Context
    # -------------------------
    context = state.get("context", {})
    if context.get("unified") == "loaded":
        interpretation["signals"].append("context_unified")

    # -------------------------
    # Overall state
    # -------------------------
    if len(interpretation["warnings"]) == 0:
        interpretation["overall"] = "healthy"
    else:
        interpretation["overall"] = "degraded"

    return interpretation

