# routes/system_semantic_analyze.py

from fastapi import APIRouter
from pydantic import BaseModel

from ops.semantic.engine import get_engine
from ops.semantic.gate import semantic_gate

router = APIRouter()


class SemanticAnalyzePayload(BaseModel):
    text: str


@router.post("/ops/semantic/analyze")
def semantic_analyze(payload: SemanticAnalyzePayload):
    """
    Semantic analyze endpoint — B16 SAFE

    - Ejecuta análisis semántico
    - Aplica semantic_gate
    - NO pasa fingerprint manualmente
    - Devuelve JSON siempre
    """

    engine = get_engine()
    if engine is None:
        return {
            "status": "error",
            "reason": "semantic_engine_unavailable",
        }

    analysis = engine.analyze(payload.text)

    gate_result = semantic_gate(
        analysis=analysis,
        source="api.semantic.analyze",
    )

    return {
        "status": "ok",
        "analysis": {
            "signals": analysis.signals.dict()
            if hasattr(analysis.signals, "dict")
            else analysis.signals,
        },
        "gate": gate_result,
    }
