# routes/system_guardrail.py

from fastapi import APIRouter
from ops.cognitive.guardrail import evaluate_guardrail
from routes.system_executive_state import get_executive_state

router = APIRouter(prefix="/system/guardrail", tags=["system"])

@router.get("/check")
def guardrail_status():
    """
    Estado actual del guardrail cognitivo.
    Endpoint READ-ONLY, sin evaluación de acciones.
    """

    executive = get_executive_state()

    return {
        "status": "ok",
        "mode": executive.get("mode"),
        "locked": executive.get("locked", True),
        "learning_enabled": False,
        "self_modification_enabled": False,
        "vector_engine_enabled": False,
        "semantic_engine": "heuristic",
        "allowed_actions": [
            "memory_read",
            "snapshot",
            "checkpoint",
            "diagnostic"
        ],
        "blocked_actions": [
            "learning",
            "self_modify",
            "agent_autonomy",
            "vector_index"
        ]
    }
