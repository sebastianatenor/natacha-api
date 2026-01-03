# routes/semantic_status.py
"""
/ops/semantic/status
Estado SEMÁNTICO VERIFICADO (AGENTE_VERAZ)

- Lee únicamente semantic_registry
- NO carga modelos
- NO infiere
- NO produce side-effects
"""

from fastapi import APIRouter
from ops.cognitive.semantic_registry import read_semantic_state

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


@router.get("/status")
def semantic_status():
    state = read_semantic_state()

    if state is None:
        return {
            "verified": True,
            "state": "uninitialized",
            "note": "no semantic events registered",
        }

    return {
        "verified": True,
        **state,
    }
