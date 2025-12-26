# routes/system_semantic_init.py
from fastapi import APIRouter
from ops.semantic.loader import init_semantic_engine

router = APIRouter(prefix="/ops/semantic", tags=["semantic"])


@router.post("/init")
def semantic_init(payload: dict | None = None):
    payload = payload or {}
    force = payload.get("force", False)

    return init_semantic_engine(force=force)
