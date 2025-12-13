from fastapi import APIRouter, Query
from unified_core.context_engine_v4 import build_context_bundle
from unified_core.memory_lazy import get_memory_state

router = APIRouter()


@router.get("/context/unified")
def unified_context(
    user_id: str,
    query: str = Query(default="", description="Consulta opcional para relevancia semántica"),
    limit: int = Query(default=20, description="Cantidad de eventos recientes a recuperar"),
    fallback: bool = Query(default=True, description="Activar fallback si hay poco contexto"),
):
    """
    Unified Context v4
    Expone explícitamente el estado de memoria para agentes externos (ChatGPT / OpenAPI).
    """

    bundle = build_context_bundle(
        user_id=user_id,
        limit=limit,
        fallback=fallback,
        query=query,
    )

    memory_state = get_memory_state()

    return {
        "status": "ok",
        "engine": "v4",
        "user_id": user_id,
        "query": query,
        "limit": limit,
        "fallback": fallback,
        "memory": {
            "present": memory_state.get("store_loaded", False),
            "items_count": memory_state.get("items_count", 0),
            "engine": memory_state.get("engine", "unknown"),
        },
        "bundle": bundle,
    }
