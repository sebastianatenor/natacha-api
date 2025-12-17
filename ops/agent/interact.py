from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ops.cognitive.cognitive_guardrail import (
    CognitiveGuardrail,
    CognitiveInput
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


# =========================
# Agent Endpoint
# =========================

@router.post(
    "/interact",
    response_model=AgentInteractResponse,
    summary="Interacción cognitiva con Natacha",
    description="Canal único y estable de conversación con el núcleo cognitivo de Natacha.",
)
def agent_interact(payload: AgentInteractRequest):
    """
    Endpoint cognitivo ejecutivo OFICIAL.

    - Usa CognitiveGuardrail
    - NO ejecuta acciones
    - SOLO propone y explica
    """

    try:
        # 1. Evaluación cognitiva
        decision = guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                project=payload.project,
                message=payload.message
            )
        )

        # 2. Respuesta base del cerebro
        result = natacha_respond(payload)
        answer_text = result.get("answer", "")

        # 3. Si hay acción propuesta, se EXPLICA (no se ejecuta)
        if decision.proposed_action:
            action = decision.proposed_action

            action_block = (
                "\n\n—\n"
                "🧠 **Nota cognitiva**:\n"
                "Detecté una posible acción implícita en tu mensaje, "
                "pero **no ejecuté nada**.\n\n"
                f"- Tipo de acción detectada: **{action.action_type.value}**\n"
                f"- Descripción: {action.description}\n\n"
                "Si querés avanzar con esto, decime explícitamente "
                "qué querés que haga o confirmá la acción."
            )

            answer_text += action_block

        return AgentInteractResponse(
            answer=answer_text,
            model_called=result.get("model_called", True),
            error=None
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error=str(e),
        )
