from typing import Dict, Any, Optional

from ops.memory.manager import user_context_manager
from ops.cognitive.cognitive_guardrail import CognitiveGuardrail, CognitiveInput
from ops.semantic.engine import semantic_engine
from ops.semantic.state import SEMANTIC_STATE


guardrail = CognitiveGuardrail()


def respond(
    user_id: str,
    message: str,
    channel: str = "unknown",
    perceived_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Respuesta cognitiva central (SAFE)

    - Evalúa guardrails
    - Analiza semántica (si está disponible)
    - Integra estado perceptivo (NO decisorio)
    - NO ejecuta acciones
    """

    # -------------------------------------------------
    # 0) Estado cognitivo vivo (objeto, NO dict)
    # -------------------------------------------------
    user_state = user_context_manager.touch(
        user_id=user_id,
        channel=channel,
    )

    # -------------------------------------------------
    # 0.1) Integración perceptiva (SAFE)
    # -------------------------------------------------
    if perceived_state:
        # Guardamos como atributo, no como dict
        try:
            setattr(user_state, "perceived_state", perceived_state)
        except Exception:
            pass  # Nunca rompemos respuesta por esto

    # -------------------------------------------------
    # 1) Guardrail cognitivo
    # -------------------------------------------------
    decision = guardrail.evaluate(
        CognitiveInput(
            user_id=user_id,
            project="LLVC",
            message=message,
        )
    )

    # -------------------------------------------------
    # 2) Análisis semántico (pasivo)
    # -------------------------------------------------
    semantic = None
    if SEMANTIC_STATE.hf_token_present:
        try:
            semantic = semantic_engine.analyze(message)
        except Exception:
            semantic = None

    # -------------------------------------------------
    # 3) Respuesta base
    # -------------------------------------------------
    answer = (
        "🧠 Canal cognitivo activo.\n\n"
        "Tu mensaje fue evaluado correctamente."
    )

    # -------------------------------------------------
    # 4) Nota semántica (informativa)
    # -------------------------------------------------
    semantic_note = None
    if semantic and semantic.model_used:
        semantic_note = {
            "intent": semantic.signals.intent,
            "risk_level": semantic.signals.risk_level,
            "confidence": semantic.signals.confidence,
            "model": semantic.model_used,
        }

    # -------------------------------------------------
    # 5) Nota cognitiva si hay acción implícita
    # -------------------------------------------------
    proposed_action = getattr(decision, "proposed_action", None)
    if proposed_action:
        answer += (
            "\n\n—\n"
            "⚠️ Nota cognitiva:\n"
            "Detecté una posible acción implícita, "
            "pero no ejecuté nada.\n\n"
            f"- Tipo: {proposed_action.action_type.value}\n"
            f"- Descripción: {proposed_action.description}\n"
        )

    return {
        "answer": answer,
        "model_called": False,
        "semantic": semantic_note,
        "channel": channel,
        "perception_attached": bool(perceived_state),
    }
