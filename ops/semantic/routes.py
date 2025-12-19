from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from unified_core.semantic_core import get_semantic_core

router = APIRouter(prefix="/ops/semantic", tags=["Semantic"])


class SemanticRequest(BaseModel):
    text: str


@router.post("/analyze")
def analyze(req: SemanticRequest):
    core = get_semantic_core()

    try:
        vector = core.embed(req.text)
        return {
            "status": "ok",
            "loaded": core.is_loaded(),
            "vector_dim": len(vector)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
