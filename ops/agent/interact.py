# ops/agent/interact.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ops.cognitive.cognitive_guardrail import (
    CognitiveGuardrail,
    CognitiveInput,
)

from ops.core.respond import respond

router = APIRouter(prefix="/agent", tags=["agent"])
guardrail = CognitiveGuardrail()


# -------------------------------------------------
# Models
# -------------------------------------------------

class AgentInteractRequest(BaseModel):
    user_id: str = "sebastian"
    project: str = "LLVC"
    message: str


class AgentInteractResponse(BaseModel):
    answer: str
    model_called: bool = False
    error: Optional[str] = None
    detail: Optional[str] = None
    perceived_state: Optional[Dict[str, Any]] = None


# -------------------------------------------------
# Helpers (SAFE)
# -------------------------------------------------

def _read_system_perception() -> Optional[Dict[str, Any]]:
    """
    Lectura REAL del estado perceptivo del sistema.
    No infiere. No razona. Lee runtime.
    """
    try:
        from routes.system_perception.router import get_latest_perception
        return get_latest_perception()
    except Exception:
        return None


# -------------------------------------------------
# Endpoint
# -------------------------------------------------

@router.post(
    "/interact",
    response_model=AgentInteractResponse,
    summary="Interacción cognitiva con Natacha (SAFE)",
    description=(
        "Canal cognitivo seguro. Evalúa intención y riesgo. "
        "Lee estado perceptivo real antes de responder."
    ),
)
def agent_interact(payload: AgentInteractRequest):
    try:
        # -------------------------------------------------
        # 0️⃣ Cognitive Boot (estado real)
        # -------------------------------------------------
        perceived_state = _read_system_perception()

        # -------------------------------------------------
        # 1️⃣ Guardrail cognitivo
        # -------------------------------------------------
        decision = guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                project=payload.project,
                message=payload.message,
            )
        )

        # -------------------------------------------------
        # 2️⃣ Respuesta centralizada
        # -------------------------------------------------
        result = respond(
            user_id=payload.user_id,
            message=payload.message,
            channel="agent",
            perceived_state=perceived_state,  # 👈 NUEVO
        )

        return AgentInteractResponse(
            answer=result.get("answer", ""),
            model_called=result.get("model_called", False),
            error=result.get("error"),
            detail=result.get("detail"),
            perceived_state=perceived_state,
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
