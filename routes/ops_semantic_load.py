from fastapi import APIRouter
from ops.semantic.engine import get_engine
from ops.cognitive.semantic_registry import register_semantic_event

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


@router.post("/load")
def load_semantic_engine():
    engine = get_engine()
    result = engine._lazy_load()

    if result.get("status") != "ok":
        register_semantic_event(
            state="error",
            confidence="high",
            source="ops_semantic_load",
        )
        return {
            "status": "error",
            "reason": result.get("reason", "engine_not_available"),
        }

    register_semantic_event(
        state="loaded",
        confidence="high",
        source="ops_semantic_load",
    )

    return {"status": "ok", "loaded": True}
