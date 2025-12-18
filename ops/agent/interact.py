# ops/agent/interact.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

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


# -------------------------------------------------
# Endpoint
# -------------------------------------------------

@router.post(
    "/interact",
    response_model=AgentInteractResponse,
    summary="Interacción cognitiva con Natacha (SAFE)",
    description=(
        "Canal cognitivo seguro. Evalúa intención y riesgo. "
        "Solo responde si está permitido."
    ),
)
def agent_interact(payload: AgentInteractRequest):
    try:
        # 1. Guardrail cognitivo
        decision = guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                project=payload.project,
                message=payload.message,
            )
        )

        # 2. Respuesta centralizada (núcleo)
        result = respond(
            user_id=payload.user_id,
            message=payload.message,
            channel="agent",
        )

        return AgentInteractResponse(
            answer=result.get("answer", ""),
            model_called=result.get("model_called", False),
            error=result.get("error"),
            detail=result.get("detail"),
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
