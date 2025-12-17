from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ops.cognitive.cognitive_guardrail import (
    CognitiveGuardrail,
    CognitiveInput
)

from routes.natacha_routes import (
    natacha_respond,
    UserMessage,
)

router = APIRouter(prefix="/agent", tags=["agent"])
guardrail = CognitiveGuardrail()


class AgentInteractRequest(BaseModel):
    user_id: str = "sebastian"
    project: str = "LLVC"
    message: str


class AgentInteractResponse(BaseModel):
    answer: str
    model_called: bool = True
    error: Optional[str] = None
    detail: Optional[str] = None


@router.post(
    "/interact",
    response_model=AgentInteractResponse,
    summary="Interacción cognitiva con Natacha",
    description="Canal único y estable de conversación con el núcleo cognitivo de Natacha.",
)
def agent_interact(payload: AgentInteractRequest):
    try:
        decision = guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                project=payload.project,
                message=payload.message
            )
        )

        user_msg = UserMessage(
            user_id=payload.user_id,
            message=payload.message,
        )

        result = natacha_respond(user_msg)

        answer_text = (result.get("answer") or "").strip()
        err = result.get("error")
        detail = result.get("detail") or result.get("debug") or None
        model_called = bool(result.get("model_called", False))

        # Nota cognitiva (solo si existe el atributo)
        proposed_action = getattr(decision, "proposed_action", None)
        if proposed_action:
            action = proposed_action
            answer_text += (
                "\n\n—\n"
                "🧠 **Nota cognitiva**:\n"
                "Detecté una posible acción implícita en tu mensaje, "
                "pero **no ejecuté nada**.\n\n"
                f"- Tipo de acción detectada: **{action.action_type.value}**\n"
                f"- Descripción: {action.description}\n\n"
                "Si querés avanzar, confirmámelo explícitamente."
            )

        return AgentInteractResponse(
            answer=answer_text,
            model_called=model_called,
            error=err,
            detail=detail,
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
