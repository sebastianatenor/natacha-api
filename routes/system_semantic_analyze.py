# routes/system_semantic_analyze.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ops.semantic.engine import get_engine
from ops.semantic.gate import semantic_gate

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


class SemanticAnalyzePayload(BaseModel):
    text: str


@router.post("/analyze")
def semantic_analyze(payload: SemanticAnalyzePayload):
    engine = get_engine()
    if engine is None:
        raise HTTPException(
            status_code=503,
            detail="Semantic engine not available",
        )

    try:
        analysis = engine.analyze(payload.text)

        gate_result = semantic_gate(
            analysis,
            source="api.semantic.analyze",
        )

        return {
            "status": "ok",
            "analysis": analysis.dict(),
            "gate": gate_result,
        }

    except Exception as e:
        # 🔒 NUNCA más text/plain
        raise HTTPException(
            status_code=500,
            detail=f"semantic_analyze failed: {type(e).__name__}: {e}",
        )
