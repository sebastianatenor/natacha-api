from typing import Optional, Dict, Any
from fastapi import APIRouter, Query

# ============================================================
# Lazy loader (Cloud Run safe)
# ============================================================

_memory_index = None


def get_memory():
    """
    Lazy + singleton access to unified memory index.
    Nunca se ejecuta en import time.
    """
    global _memory_index
    if _memory_index is None:
        from unified_core.memory_lazy import get_memory_index
        _memory_index = get_memory_index()
    return _memory_index


router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])


# ============================================================
# Routes
# ============================================================

@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    memory = get_memory()
    memory_id = memory.save_raw(payload)
    return {"status": "raw_saved", "memory_id": memory_id}


@router.post("/consolidate")
def memory_consolidate(user_id: Optional[str] = None):
    memory = get_memory()
    result = memory.consolidate(user_id=user_id)
    if not result:
        return {"status": "empty", "result": None}
    return {"status": "ok", "result": result}


@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    memory = get_memory()
    items = memory.list_recent(user_id=user_id, limit=limit)
    return {"count": len(items), "items": items}


@router.post("/system")
def memory_system(payload: Dict[str, Any]):
    memory = get_memory()
    note = payload.get("note", "")
    version = payload.get("version", "v1")
    memory.save_system_rule(note, version)
    return {"status": "system_saved", "version": version}


@router.get("/context_bundle")
def memory_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = Query(20, ge=1, le=200),
    include_global_fallback: bool = True,
):
    memory = get_memory()
    bundle = memory.build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
        include_global_fallback=include_global_fallback,
    )
    return bundle
