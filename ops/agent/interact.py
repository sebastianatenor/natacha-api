# ops/agent/interact.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import unicodedata

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
# Helpers
# -------------------------------------------------

def _normalize(text: str) -> str:
    return (
        unicodedata
        .normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )


def _is_state_question(message: str) -> bool:
    """
    Detección robusta de consulta de estado.
    Si el mensaje contiene la palabra 'estado',
    se considera introspección del sistema.
    """
    msg = _normalize(message)
    return "estado" in msg


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


def _fallback_narrative(perception: Dict[str, Any]) -> str:
    return (
        "🧠 **Estado actual del sistema**\n\n"
        f"• Servicio: {perception.get('service')}\n"
        f"• Revisión: {perception.get('revision')}\n"
        f"• Memoria canónica: "
        f"{'activa' if perception.get('memory', {}).get('exists') else 'no disponible'}\n"
        f"• Timeline eventos: {perception.get('timeline', {}).get('events_total')}\n"
        f"• Motor semántico cargado: "
        f"{perception.get('semantic', {}).get('loaded', False)}\n\n"
        "Sistema estable. Sin degradaciones activas."
    )


# -------------------------------------------------
# Endpoint
# -------------------------------------------------

@router.post("/interact", response_model=AgentInteractResponse)
def agent_interact(payload: AgentInteractRequest):
    try:
        # -------------------------------------------------
        # 0) Percepción real
        # -------------------------------------------------
        perceived_state = _read_system_perception()
        is_state = _is_state_question(payload.message)

        # -------------------------------------------------
        # 1) Guardrail (siempre primero)
        # -------------------------------------------------
        guardrail.evaluate(
            CognitiveInput(
                user_id=payload.user_id,
                project=payload.project,
                message=payload.message,
            )
        )

        # -------------------------------------------------
        # 2) RESPUESTA DE ESTADO (FORZADA)
        # -------------------------------------------------
        if perceived_state and is_state:
            try:
                from ops.narrative.composer import compose_system_narrative
                narrative = compose_system_narrative(perceived_state)
            except Exception:
                narrative = _fallback_narrative(perceived_state)

            return AgentInteractResponse(
                answer=narrative,
                model_called=False,
                perceived_state=perceived_state,
            )

        # -------------------------------------------------
        # 3) RESPUESTA NORMAL
        # -------------------------------------------------
        result = respond(
            user_id=payload.user_id,
            message=payload.message,
            channel="agent",
            perceived_state=perceived_state,
        )

        return AgentInteractResponse(
            answer=result.get("answer", ""),
            model_called=result.get("model_called", False),
            perceived_state=perceived_state,
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
