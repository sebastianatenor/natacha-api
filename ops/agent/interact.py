# ops/agent/interact.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ops.cognitive.cognitive_guardrail import (
    CognitiveGuardrail,
    CognitiveInput,
    MemoryLevel
)
from routes.natacha_routes import natacha_respond

router = APIRouter(
    prefix="/agent",
    tags=["agent"]
)

guardrail = CognitiveGuardrail()

# =========================
# Executive Contract Models
# =========================

class AgentInteractRequest(BaseModel):
    user_id: str = "sebastian"
    project: str = "LLVC"
    message: str


class AgentInteractResponse(BaseModel):
    answer: str
    model_called: bool = True
    error: Optional[str] = None


@router.post(
    "/interact",
    response_model=AgentInteractResponse,
    summary="Interacción cognitiva con Natacha",
    description="Canal único y estable de conversación con el núcleo cognitivo de Natacha.",
)
def agent_interact(payload: AgentInteractRequest):
    """
    Endpoint cognitivo ejecutivo OFICIAL.

    Flujo:
    1. Guardrail evalúa intención y riesgo
    2. Decide memoria / aclaración / warnings
    3. El cerebro responde bajo esas reglas
    """

    try:
        decision = guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                message=payload.message,
                project=payload.project,
            )
        )

        # Si requiere aclaración explícita
        if decision.needs_clarification:
            clarification_note = (
                "Antes de avanzar, necesito que aclaremos esto juntos."
            )
        else:
            clarification_note = ""

        result = natacha_respond(payload)

        answer = result.get("answer", "")

        if clarification_note:
            answer = f"{answer}\n\n{clarification_note}"

        return AgentInteractResponse(
            answer=answer,
            model_called=result.get("model_called", True),
            error=result.get("error"),
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error=str(e),
        )
