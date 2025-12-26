# ops/cognitive/autonomy_manifest.py
"""
B12 — Autonomy Manifest
Defines which actions the agent is allowed to execute autonomously.
THIS IS A HARD SAFETY BOUNDARY.
"""

AUTONOMY_VERSION = "B12.1"

ALLOWED_AUTONOMOUS_ACTIONS = {
    "reload_semantic": {
        "description": "Reload semantic engine runtime",
        "risk": "low",
        "reversible": True,
    },
    "reload_semantic_runtime": {
        "description": "Force reload semantic runtime loader",
        "risk": "low",
        "reversible": True,
    },
    "rebuild_vector_index": {
        "description": "Rebuild semantic vector index from memory",
        "risk": "medium",
        "reversible": True,
    },
    "reload_memory_index": {
        "description": "Reload in-memory memory index",
        "risk": "low",
        "reversible": True,
    },
}

def is_action_allowed(action: str) -> bool:
    return action in ALLOWED_AUTONOMOUS_ACTIONS


def get_allowed_actions() -> dict:
    return ALLOWED_AUTONOMOUS_ACTIONS
