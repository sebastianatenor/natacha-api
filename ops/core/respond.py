# ops/core/respond.py

from typing import Dict, Any, Optional

from ops.memory.manager import user_context_manager
from ops.semantic.engine import get_engine
from ops.semantic.state import SEMANTIC_STATE
from ops.cognitive.guardrail import evaluate_guardrail
from ops.cognitive.veracity import check_veracity
from ops.system.runtime_probe import runtime_verification

def respond(
    user_id: str,
    message: str,
    channel: str = "unknown",
    perceived_state: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Respuesta cognitiva central (PRE-ML SAFE)

    - NO ejecuta acciones
    - NO usa CognitiveGuardrail legacy
    - Solo evalúa estado ejecutivo pasivo
    """

    # -------------------------------------------------
    # 0) Estado de usuario (contextual, no decisorio)
    # -------------------------------------------------
    user_state = user_context_manager.touch(
        user_id=user_id,
        channel=channel,
    )

    if perceived_state:
        try:
            setattr(user_state, "perceived_state", perceived_state)
        except Exception:
            pass

    # -------------------------------------------------
    # 1) Guardrail PRE-ML (pasivo, sin side effects)
    # -------------------------------------------------
    _ = evaluate_guardrail(
        executive_state=perceived_state or {},
        action="context_read"
    )

    # -------------------------------------------------
    # 2) Semántica (si está habilitada)
    # -------------------------------------------------
    semantic_note = None
    engine = get_engine()

    if engine and SEMANTIC_STATE.hf_token_present:
        try:
            semantic = engine.analyze(message)
            semantic_note = {
                "intent": semantic.signals.intent,
                "risk_level": semantic.signals.risk_level,
                "confidence": semantic.signals.confidence,
                "model": semantic.model_used,
            }
        except Exception:
            semantic_note = None

    # -------------------------------------------------
    # 3) Respuesta base (SAFE)
    # -------------------------------------------------
    answer = (
        "🧠 Canal cognitivo activo.\n\n"
        "El sistema evaluó tu mensaje correctamente."
    )

    # -------------------------------------------------
    # 4) Veracidad (AGENTE_VERAZ – enforcement)
    # -------------------------------------------------
    runtime = runtime_verification()

    verified = runtime.get("health", False) and runtime.get("system_state", False)

    answer, blocked = check_veracity(
        answer=answer,
        verified=verified
    )

    return {
        "answer": answer,
        "model_called": False,
        "semantic": semantic_note,
        "channel": channel,
        "perception_attached": bool(perceived_state),
        "veracity": {
            "verified": verified,
            "blocked": blocked
        }
        "runtime_verified": runtime
    }
