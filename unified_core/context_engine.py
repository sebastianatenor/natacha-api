"""
context_engine.py — Natacha Unified Core (v7)
---------------------------------------------

Core unificado del cerebro de Natacha.
"""

from typing import Optional, Dict, Any

# -------------------------------------------------------------
# Unified memory access (LAZY + SINGLETON)
# -------------------------------------------------------------
from unified_core.memory_lazy import get_memory_index

memory = get_memory_index()

# -------------------------------------------------------------
# Estado afectivo
# -------------------------------------------------------------
try:
    from ops.affective_train import get_affective_state
except Exception:
    def get_affective_state():
        return {"status": "unavailable"}

# -------------------------------------------------------------
# Estado cognitivo
# -------------------------------------------------------------
try:
    from ops.cognitive_evolution import get_cognitive_state
except Exception:
    def get_cognitive_state():
        return {"status": "unavailable"}

# -------------------------------------------------------------
# Reglas del sistema
# -------------------------------------------------------------
def _load_system_rule(version: str = "core-v1"):
    return memory.get_system_rule(version)

# -------------------------------------------------------------
# Summary consolidado
# -------------------------------------------------------------
def _load_summary(user_id: Optional[str]):
    return memory.get_summary(user_id)

# -------------------------------------------------------------
# Context Engine v7
# -------------------------------------------------------------
def build_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = 20,
    include_global_fallback: bool = True,
) -> Dict[str, Any]:

    system_rule = _load_system_rule("core-v1")

    # Semantic summary
    try:
        from natacha_core import semantic_memory_v2
        semantic_summary = semantic_memory_v2.summarize(
            user_id=user_id,
            project=None,
            q="estado general",
            limit=7,
        )
    except Exception as e:
        semantic_summary = {
            "error": str(e),
            "summary": None,
            "items": [],
        }

    # Recent memories
    try:
        recent_items = memory.list_recent(
            user_id=user_id,
            limit=recent_limit,
        )
    except Exception as e:
        recent_items = [{"error": str(e)}]

    affective_state = get_affective_state()
    cognitive_state = get_cognitive_state()

    return {
        "status": "ok",
        "engine": "v7-unified",
        "user_id": user_id,
        "system_rule": system_rule,
        "summary": semantic_summary,
        "recent": {
            "count": len(recent_items),
            "items": recent_items,
        },
        "affective_state": affective_state,
        "cognitive_state": cognitive_state,
    }
