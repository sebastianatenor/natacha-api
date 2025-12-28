from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])

class SemanticAnalyzePayload(BaseModel):
    text: str

@router.post("/analyze")
def semantic_analyze(payload: SemanticAnalyzePayload):
    # 🔒 PASSTHROUGH SAFE MODE
    return {
        "status": "ok",
        "text": payload.text,
        "note": "semantic analyze temporarily in safe passthrough mode"
    }
