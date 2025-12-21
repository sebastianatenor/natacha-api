from fastapi import APIRouter
from ops.cognitive.state_registry import write_cognitive_state
import os

router = APIRouter(prefix="/ops/semantic", tags=["Semantic"])

@router.post("/analyze")
def analyze(payload: dict):
    text = payload.get("text", "")
    if not text:
        return {"status": "error", "detail": "text required"}

    from unified_core.semantic_core import get_semantic_core
    core = get_semantic_core()
    core.ensure_loaded()

    # 🔐 PERSISTIR ESTADO SEMÁNTICO (CLAVE)
    write_cognitive_state(
        subsystem="semantic",
        state="loaded",
        revision=os.getenv("K_REVISION"),
        confidence="high",
        details={
            "model": "sentence-transformers/all-MiniLM-L6-v2",
            "trigger": "semantic_analyze"
        }
    )

    try:
        from ops.cognitive.write_state import write_cognitive_state

        write_cognitive_state(
            subsystem="semantic",
            state="loaded",
            confidence="high",
            details={"source": "semantic_analyze"}
        )
    except Exception as e:
        print(f"[SEMANTIC][WARN] cognitive state not registered: {e}")

    vec = core.embed(text)
    return {
        "status": "ok",
        "loaded": True,
        "vector_dim": len(vec)
    }
