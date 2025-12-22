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
    Respuesta cognitiva central (SAFE):

    - Evalúa guardrails
    - Analiza semántica (si está disponible)
    - Integra estado perceptivo (si existe)
    - NO ejecuta acciones
    - LLM es opcional y externo
    """

    # -------------------------------------------------
    # 0) Estado cognitivo vivo (RAM)
    # -------------------------------------------------
    user_state = user_context_manager.touch(
        user_id=user_id,
        channel=channel,
    )

    # -------------------------------------------------
    # 0.1) Integración perceptiva (NO decisoria)
    # -------------------------------------------------
    # Esto fija el "punto de partida cognitivo"
    # antes de cualquier respuesta.
    if perceived_state:
        user_state["perceived_state"] = perceived_state

    # -------------------------------------------------
    # 1) Guardrail cognitivo (autoridad máxima)
    # -------------------------------------------------
    decision = guardrail.evaluate(
        CognitiveInput(
            user_id=user_id,
            project="LLVC",
            message=message,
        )
    )

    # -------------------------------------------------
    # 2) Análisis semántico (PASIVO)
    # -------------------------------------------------
    semantic = None
    if SEMANTIC_STATE.hf_token_present:
        try:
            semantic = semantic_engine.analyze(message)
        except Exception:
            semantic = None

    # -------------------------------------------------
    # 3) Respuesta base estable
    # -------------------------------------------------
    answer = (
        "🧠 Canal cognitivo activo.\n\n"
        "Tu mensaje fue evaluado correctamente."
    )

    # -------------------------------------------------
    # 3.1) Transparencia perceptiva (si existe)
    # -------------------------------------------------
    if perceived_state:
        answer += (
            "\n\n—\n"
            "📍 **Estado perceptivo actual**:\n"
            f"- Servicio: {perceived_state.get('service')}\n"
            f"- Revisión: {perceived_state.get('revision')}\n"
            f"- Memoria canónica: "
            f"{'activa' if perceived_state.get('memory', {}).get('exists') else 'no disponible'}\n"
            f"- Motor semántico cargado: "
            f"{perceived_state.get('semantic', {}).get('loaded', False)}"
        )

    # -------------------------------------------------
    # 4) Anotación semántica (NO decisoria)
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
            "⚠️ **Nota cognitiva**:\n"
            "Detecté una posible acción implícita, "
            "pero **no ejecuté nada**.\n\n"
            f"- Tipo: **{proposed_action.action_type.value}**\n"
            f"- Descripción: {proposed_action.description}\n\n"
            "Confirmá explícitamente si querés avanzar."
        )

    return {
        "answer": answer,
        "model_called": False,
        "semantic": semantic_note,
        "channel": channel,
        "perception_attached": bool(perceived_state),
    }
