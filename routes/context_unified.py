# routes/context_unified.py

from fastapi import APIRouter, Query
from unified_core.context_engine_v4 import build_context_bundle
from unified_core.memory_lazy import get_memory_index

router = APIRouter()


@router.get("/context/unified")
def unified_context(
    user_id: str,
    query: str = Query(default="", description="Consulta opcional para relevancia semántica"),
    limit: int = Query(default=20, description="Cantidad de eventos recientes"),
    fallback: bool = Query(default=True, description="Activar fallback si hay poco contexto"),
):
    """
    Contexto unificado — FUENTE OFICIAL DE MEMORIA DEL SISTEMA
    """

    memory = get_memory_index()
    bundle = build_context_bundle(
        user_id=user_id,
        limit=limit,
        fallback=fallback,
        query=query,
    )

    return {
        "status": "ok",
        "engine": "context-unified-v4",
        "memory": {
            "store_loaded": memory.store_loaded,
            "store_path": memory.store_path,
            "items_count": len(memory._items) if memory._items else 0,
        },
        "bundle": bundle,
    }
