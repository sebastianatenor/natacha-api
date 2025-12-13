from fastapi import APIRouter, Query
from unified_core.context_engine_v4 import build_context_bundle

router = APIRouter()


@router.get("/context/unified")
def unified_context(
    user_id: str,
    query: str = Query(default="", description="Consulta opcional para relevancia semántica"),
    limit: int = Query(default=20, description="Cantidad de eventos recientes a recuperar"),
    fallback: bool = Query(default=True, description="Activar fallback si hay poco contexto"),
):
    """
    Unified Context v4 – versión estable EXACTAMENTE alineada con la firma real.
    No agrega parámetros inválidos.
    """

    bundle = build_context_bundle(
        user_id=user_id,
        limit=limit,
        fallback=fallback,
        query=query,
    )

    return {
        "status": "ok",
        "engine": "v4",
        "user_id": user_id,
        "query": query,
        "limit": limit,
        "fallback": fallback,
        "bundle": bundle,
    }
