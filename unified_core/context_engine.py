"""
context_engine.py — Natacha Unified Core (v7)
---------------------------------------------

Core unificado del cerebro de Natacha.

Objetivo:
- Integrar memoria cruda + memoria semántica + estado emocional + estado cognitivo.
- Ser 100% compatible con el contexto legacy mientras migramos.
"""

from typing import Optional, Dict, Any

# -------------------------------------------------------------
# Imports reales desde el motor existente
# -------------------------------------------------------------
from memory_engine import (
    list_recent_memories,
    consolidate_memory,
    COL_SYSTEM,
    COL_SUMMARY,
    db,
)

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
    doc = db.collection(COL_SYSTEM).document(version).get()
    return doc.to_dict() if doc.exists else None

# -------------------------------------------------------------
# Summary consolidado (por usuario o global)
# -------------------------------------------------------------
def _load_summary(user_id: Optional[str]):
    key = user_id or "global"
    doc = db.collection(COL_SUMMARY).document(key).get()
    if doc.exists:
        return doc.to_dict()

    if user_id:
        # fallback global
        global_doc = db.collection(COL_SUMMARY).document("global").get()
        if global_doc.exists:
            return global_doc.to_dict()

    return None

# -------------------------------------------------------------
#  Context Engine v7 (FINAL)
# -------------------------------------------------------------
def build_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = 20,
    include_global_fallback: bool = True,
) -> Dict[str, Any]:

    # 1) Regla del sistema
    system_rule = _load_system_rule("core-v1")

    # 2) Summary semántico via semantic_memory_v2
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

    # 3) Memorias recientes (raw)
    try:
        recent_items = list_recent_memories(
            user_id=user_id,
            limit=recent_limit,
        )
    except Exception as e:
        recent_items = [{"error": str(e)}]

    # 4) Estado emocional
    try:
        affective_state = get_affective_state()
    except Exception:
        affective_state = {"status": "unavailable"}

    # 5) Estado cognitivo
    try:
        cognitive_state = get_cognitive_state()
    except Exception:
        cognitive_state = {"status": "unavailable"}

    # ----------------------------
    # 6) Bundle final unificado (v7)
    # ----------------------------
    bundle = {
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

    return bundle
