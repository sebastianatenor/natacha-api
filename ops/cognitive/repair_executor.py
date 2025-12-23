import os
from typing import Dict, Any

from ops.cognitive.repair_log import log_repair_proposal


def execute_repair(drift: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ejecuta reparación SOLO si el sistema está armado.
    """
    mode = os.getenv("SELF_REPAIR_MODE", "proposal_only")

    if mode != "armed":
        return {
            "status": "blocked",
            "detail": "Self-repair not armed",
            "mode": mode,
        }

    # --- Ejemplo de reparaciones permitidas ---
    actions = []

    if drift.get("memory_expected") and not drift.get("memory_exists"):
        actions.append("restore_memory")

    if drift.get("semantic_expected") and not drift.get("semantic_loaded"):
        actions.append("reload_semantic")

    if not actions:
        return {
            "status": "noop",
            "detail": "No repairable drift found",
        }

    # ⚠️ TODAVÍA NO EJECUTAMOS NADA REAL
    log_repair_proposal(
        drift={
            **drift,
            "executed_actions": actions,
        },
        baseline=baseline,
        level="EXECUTION_SIMULATION",
    )

    return {
        "status": "simulated",
        "actions": actions,
        "confidence": "high",
    }
