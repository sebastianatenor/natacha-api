# routes/ops_semantic_status.py
"""
/ops/semantic/status
Estado semántico VERIFICADO — AGENTE_VERAZ

Fuente:
- ops.cognitive.semantic_registry
"""

from fastapi import APIRouter
from ops.cognitive.semantic_registry import read_semantic_state

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


@router.get("/status")
def semantic_status():
    state = read_semantic_state()

    if state is None:
        return {
            "verified": False,
            "state": "unknown",
            "reason": "semantic_not_initialized",
        }

    return {
        "verified": True,
        **state,
    }
