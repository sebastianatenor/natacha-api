# ops/agent/interact.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
import unicodedata

from ops.cognitive.guardrail import evaluate_guardrail
from ops.cognitive.semantic_decider import decide_semantic_signal
from ops.cognitive.permission_gate import permission_allowed
from ops.cognitive.action_executor import execute_confirmed_action
from ops.cognitive.pending_intent import (
    set_pending_intent,
    get_pending_intent,
    clear_pending_intent,
)

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
        .strip()
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


def _is_explicit_confirmation(message: str) -> bool:
    msg = _normalize(message)
    return msg in (
        "confirmo",
        "confirmar",
        "si",
        "sí",
        "ok",
        "adelante",
        "adelante hacelo",
        "hacelo",
    )


def _blocked_by_semantic(signal: Dict[str, Any]) -> bool:
    return (
        signal.get("intent") == "implicit_action"
        and signal.get("risk_level") == "high"
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

        # -------------------------------------------------
        # 1️⃣ Guardrail ejecutivo PRE-ML (pasivo)
        # -------------------------------------------------
        _ = evaluate_guardrail(
            executive_state=baseline or {},
            action="context_read",
        )

        # -------------------------------------------------
        # 2️⃣ Pregunta de estado (NO semántica)
        # -------------------------------------------------
        if perception and _is_state_question(payload.message):
            return AgentInteractResponse(
                answer="Estado del sistema disponible.",
                model_called=False,
                perceived_state={
                    "baseline": baseline,
                    "perception": perception,
                },
            )

        # -------------------------------------------------
        # 3️⃣ Confirmación explícita (E + F)
        # -------------------------------------------------

        pending = get_pending_intent()

        # ✅ Confirmación explícita SIN intención pendiente
        if not pending and _is_explicit_confirmation(payload.message):
            return AgentInteractResponse(
                answer="⚠️ No hay ninguna acción pendiente para confirmar.",
                model_called=False,
            )

        # ✅ Confirmación explícita CON intención pendiente
        if pending and _is_explicit_confirmation(payload.message):
            clear_pending_intent()
            signal = pending["signal"]

            if not permission_allowed(payload.user_id, signal):
                return AgentInteractResponse(
                    answer="⛔ No tenés permisos para ejecutar esta acción.",
                    model_called=False,
                    perceived_state={
                        "blocked": "permission_denied",
                        "signal": signal,
                    },
                )

            execution = execute_confirmed_action(signal)

            return AgentInteractResponse(
                answer="🚀 Acción ejecutada correctamente.",
                model_called=False,
                perceived_state={
                    "execution": execution,
                },
            )

        # -------------------------------------------------
        # 4️⃣ Decisión semántica (A + B)
        # -------------------------------------------------
        decision = decide_semantic_signal(payload.message)
        signal = decision.get("signal")

        if signal and _blocked_by_semantic(signal):
            set_pending_intent(signal)

            return AgentInteractResponse(
                answer=(
                    "⚠️ Detecté una intención implícita de acción automática.\n\n"
                    "Para continuar, confirmá explícitamente escribiendo:\n"
                    "👉 “confirmo” o “adelante, hacelo”"
                ),
                model_called=False,
                perceived_state={
                    "semantic": signal,
                    "semantic_decision": decision,
                    "pending": True,
                },
            )

        # -------------------------------------------------
        # 5️⃣ Respuesta normal (AGENTE_VERAZ)
        # -------------------------------------------------
        result = respond(
            user_id=payload.user_id,
            message=payload.message,
            channel="agent",
            perceived_state=None,
        )

        return AgentInteractResponse(
            answer=result.get("answer", ""),
            model_called=result.get("model_called", False),
        )

    except Exception as e:
        return AgentInteractResponse(
            answer="",
            model_called=False,
            error="agent_interact_exception",
            detail=str(e),
        )
