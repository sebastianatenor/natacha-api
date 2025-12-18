from typing import Dict, Any

from ops.cognitive.cognitive_guardrail import CognitiveGuardrail, CognitiveInput
from ops.semantic.engine import semantic_engine
from ops.semantic.state import SEMANTIC_STATE


guardrail = CognitiveGuardrail()


def respond(
    user_id: str,
    message: str,
    channel: str = "unknown",
) -> Dict[str, Any]:
    """
    Respuesta cognitiva central (SAFE):
    - Evalúa guardrails
    - Analiza semántica (si está disponible)
    - NO ejecuta acciones
    - LLM es opcional y externo
    """

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
    }
