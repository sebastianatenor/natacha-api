from fastapi import APIRouter, Query
from typing import Optional

from unified_core.context_engine import build_context_bundle

router = APIRouter(prefix="/context", tags=["context-unified"])


@router.get("/unified")
def unified_context(
    user_id: Optional[str] = Query(None),
    recent_limit: int = Query(20, ge=1, le=200)
):
    """
    Endpoint oficial del motor unificado de contexto (v7).
    Totalmente compatible y seguro.
    """
    bundle = build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
        include_global_fallback=True,
    )

    return {
        "status": "ok",
        "engine_version": "v7",
        "bundle": bundle,
    }
