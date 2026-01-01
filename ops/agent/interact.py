# ops/agent/interact.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import unicodedata

from ops.cognitive.guardrail import evaluate_guardrail

from ops.core.respond import respond
from ops.system.perception_provider import read_system_perception
from ops.system.baseline_provider import read_baseline
from ops.cognitive.boot_reader import read_last_cognitive_boot

router = APIRouter(prefix="/agent", tags=["agent"])


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
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )


def _is_state_question(message: str) -> bool:
    msg = _normalize(message)
    return any(
        k in msg
        for k in (
            "estado",
            "estado actual",
            "como estas",
            "cual es tu estado",
            "estado antes de responder",
        )
    )


def _fallback_narrative(perception: Dict[str, Any]) -> str:
    return (
        "🧠 Estado actual del sistema\n\n"
        f"• Servicio: {perception.get('service')}\n"
        f"• Revisión: {perception.get('revision')}\n"
        f"• Entorno: {perception.get('environment')}\n"
        f"• Memoria canónica: "
        f"{'activa' if perception.get('memory', {}).get('exists') else 'no disponible'}\n"
        f"• Eventos en timeline: {perception.get('timeline', {}).get('events_total')}\n"
        f"• Motor semántico cargado: "
        f"{perception.get('semantic', {}).get('loaded', False)}\n\n"
        "Sistema operativo y estable."
    )


# -------------------------------------------------
# Endpoint
# -------------------------------------------------

@router.post("/interact", response_model=AgentInteractResponse)
def agent_interact(payload: AgentInteractRequest):
    try:
        # -------------------------------------------------
        # 0️⃣ Estado REAL del sistema
        # -------------------------------------------------
        perception = read_system_perception()
        baseline = read_baseline()

        if perception is None:
            perception = read_last_cognitive_boot()

        is_state = _is_state_question(payload.message)

        # -------------------------------------------------
        # 1️⃣ Guardrail ejecutivo PRE-ML (pasivo)
        # -------------------------------------------------
        _ = evaluate_guardrail(
            executive_state=baseline or {},
            action="context_read"
        )

        # -------------------------------------------------
        # 2️⃣ RESPUESTA DE ESTADO
        # -------------------------------------------------
        if perception and is_state:
            drift = {
                "revision_changed": (
                    baseline.get("revision") != perception.get("revision")
                    if baseline else None
                ),
                "semantic_expected": (
                    baseline.get("semantic", {}).get("expected_loaded")
                    if baseline else None
                ),
                "semantic_loaded": perception.get("semantic", {}).get("loaded"),
            }

            try:
                from ops.narrative.composer import compose_system_narrative
                narrative = compose_system_narrative(perception)

                if not isinstance(narrative, str):
                    narrative = _fallback_narrative(perception)

            except Exception:
                narrative = _fallback_narrative(perception)

            return AgentInteractResponse(
                answer=narrative,
                model_called=False,
                perceived_state={
                    "baseline": baseline,
                    "perception": perception,
                    "drift": drift,
                },
            )

        # -------------------------------------------------
        # 3️⃣ RESPUESTA NORMAL
        # -------------------------------------------------
        result = respond(
            user_id=payload.user_id,
            message=payload.message,
            channel="agent",
            perceived_state=perception,
        )

        return AgentInteractResponse(
            answer=result.get("answer", ""),
            model_called=result.get("model_called", False),
            perceived_state={
                "baseline": baseline,
                "perception": perception,
            },
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
