from fastapi import APIRouter, Body
from typing import Dict, Any

from ops.semantic.engine import semantic_engine
from ops.semantic.state import SEMANTIC_STATE

router = APIRouter(
    prefix="/ops/semantic",
    tags=["semantic-debug"]
)


@router.post("/analyze")
def semantic_analyze(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    DEBUG semántico PASIVO.
    - NO ejecuta acciones
    - NO llama LLMs
    - NO escribe memoria
    """

    text = payload.get("text")
    if not text:
        return {
            "status": "error",
            "detail": "Missing 'text'"
        }

    if not SEMANTIC_STATE.loaded:
        return {
            "status": "disabled",
            "hf_token_present": SEMANTIC_STATE.hf_token_present,
            "semantic_loaded": False,
            "detail": "Semantic engine not initialized"
        }

    try:
        analysis = semantic_engine.analyze(text)
        return {
            "status": "ok",
            "model_used": analysis.model_used,
            "signals": {
                "intent": analysis.signals.intent,
                "risk_level": analysis.signals.risk_level,
                "confidence": analysis.signals.confidence,
            },
            "raw": analysis.raw,
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
