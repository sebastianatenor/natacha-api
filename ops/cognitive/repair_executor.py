# ops/cognitive/repair_executor.py
"""
B12.2 — Real Self-Repair Executor
Executes ONLY whitelisted autonomous actions.
This module is SAFETY-CRITICAL.
"""

from datetime import datetime
from typing import Dict, Any

from ops.cognitive.autonomy_manifest import is_action_allowed
from ops.timeline.writer import write_event


class RepairExecutionError(Exception):
    pass


def _log(action: str, status: str, details: Dict[str, Any] | None = None):
    write_event(
        kind="self_repair",
        subsystem="executor",
        state=status,
        confidence="high",
        details={
            "action": action,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# ================================================================
# ACTION IMPLEMENTATIONS (SAFE ONLY)
# ================================================================

def _reload_semantic():
    from ops.semantic.runtime_loader import load_semantic_engine
    return load_semantic_engine()


def _reload_semantic_runtime():
    from ops.semantic.runtime_loader import load_semantic_engine
    return load_semantic_engine()


def _rebuild_vector_index():
    from unified_core.memory_lazy import reset_memory_index
    reset_memory_index()
    return True


def _reload_memory_index():
    from unified_core.memory_lazy import reset_memory_index
    reset_memory_index()
    return True


ACTION_HANDLERS = {
    "reload_semantic": _reload_semantic,
    "reload_semantic_runtime": _reload_semantic_runtime,
    "rebuild_vector_index": _rebuild_vector_index,
    "reload_memory_index": _reload_memory_index,
}


# ================================================================
# PUBLIC EXECUTION ENTRYPOINT
# ================================================================

def execute_repair(drift: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes a repair action if and only if:
    - Drift exists
    - Action is recommended
    - Action is allowed by autonomy manifest
    """

    action = drift.get("recommended_action")

    if not action:
        return {
            "status": "noop",
            "detail": "No recommended action",
        }

    if not is_action_allowed(action):
        _log(action, "blocked", {"reason": "action_not_allowed"})
        return {
            "status": "blocked",
            "action": action,
            "reason": "Action not allowed by autonomy manifest",
        }

    handler = ACTION_HANDLERS.get(action)

    if not handler:
        _log(action, "error", {"reason": "handler_missing"})
        raise RepairExecutionError(f"No handler for action: {action}")

    _log(action, "started")

    try:
        result = handler()

        _log(action, "completed", {"result": result})

        return {
            "status": "executed",
            "action": action,
            "result": result,
        }

    except Exception as e:
        _log(action, "failed", {"error": str(e)})
        raise RepairExecutionError(str(e))
