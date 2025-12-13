from typing import Optional, Dict, Any

from fastapi import APIRouter, Query

# Motor de memoria unificado (lazy, Cloud Run safe)
from unified_core.memory_lazy import get_memory_index


# Instancia singleton lazy (no bloquea startup)
memory = get_memory_index()

router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])


@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    """
    Guarda una memoria cruda normalizada.
    """
    memory_id = memory.save_raw(payload)
    return {
        "status": "raw_saved",
        "memory_id": memory_id,
    }


@router.post("/consolidate")
def memory_consolidate(user_id: Optional[str] = None):
    """
    Consolida memorias (global o por usuario).
    """
    result = memory.consolidate(user_id=user_id)

    if not result:
        return {
            "status": "empty",
            "result": None,
        }

    return {
        "status": "ok",
        "result": result,
    }


@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    """
    Lista memorias crudas recientes.
    """
    items = memory.list_recent(
        user_id=user_id,
        limit=limit,
    )

    return {
        "count": len(items),
        "items": items,
    }


@router.post("/system")
def memory_system(payload: Dict[str, Any]):
    """
    Guarda una regla de sistema (ej: protocolos, contratos, reglas core).
    """
    note = payload.get("note", "")
    version = payload.get("version", "v1")

    memory.save_system_rule(note, version)

    return {
        "status": "system_saved",
        "version": version,
    }


@router.get("/context_bundle")
def memory_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = Query(20, ge=1, le=200),
    include_global_fallback: bool = True,
):
    """
    Devuelve el bundle de contexto unificado (v7):
    - regla de sistema
    - summary semántico
    - memorias recientes
    - estado afectivo
    - estado cognitivo
    """
    bundle = memory.build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
        include_global_fallback=include_global_fallback,
    )

    return bundle
