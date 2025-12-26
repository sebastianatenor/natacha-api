# routes/system_semantic_analyze.py

from fastapi import APIRouter
from pydantic import BaseModel

from ops.semantic import get_engine, semantic_status
from ops.semantic.gate import semantic_gate

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


class SemanticRequest(BaseModel):
    text: str


@router.post("/analyze")
def semantic_analyze(payload: SemanticRequest):
    engine = get_engine()

    if engine is None:
        return {
            "status": "disabled",
            "semantic": None,
            "engine": semantic_status(),
        }

    analysis = engine.analyze(payload.text)

    gate_result = semantic_gate(
        analysis=analysis,
        source="ops.semantic.analyze",
    )

    return {
        "status": "ok",
        "semantic": analysis.dict(),
        "gate": gate_result,
        "engine": semantic_status(),
    }
