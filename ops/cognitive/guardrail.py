# ops/cognitive/guardrail.py

from typing import Dict

PRE_ML_BLOCKED_ACTIONS = {
    "semantic_write",
    "vector_index",
    "self_modify",
    "agent_autonomy",
    "learning",
    "auto_reflection"
}

PRE_ML_ALLOWED_ACTIONS = {
    "memory_read",
    "memory_write_executive",
    "snapshot",
    "checkpoint",
    "context_read",
    "context_write",
    "diagnostic",
}

def evaluate_guardrail(
    executive_state: Dict,
    action: str
) -> Dict:
    """
    Decide si una acción está permitida según el estado ejecutivo.
    """

    mode = executive_state.get("mode")

    # Default: deny
    decision = {
        "allowed": False,
        "mode": mode,
        "action": action,
        "reason": "action_not_allowed"
    }

    if mode == "pre-ml-unified":
        if action in PRE_ML_ALLOWED_ACTIONS:
            decision["allowed"] = True
            decision["reason"] = "allowed_pre_ml"
        elif action in PRE_ML_BLOCKED_ACTIONS:
            decision["reason"] = "blocked_pre_ml"
        else:
            decision["reason"] = "unknown_action"

    else:
        # Future modes (ml-active, hybrid, etc)
        decision["allowed"] = True
        decision["reason"] = "allowed_non_pre_ml"

    return decision
