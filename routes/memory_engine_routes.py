from typing import Optional, Dict, Any
from fastapi import APIRouter, Query, HTTPException

# ============================================================
# Unified Lazy Memory Index (SINGLE SOURCE OF TRUTH)
# ============================================================

try:
    from unified_core.memory_lazy import get_memory_index
    memory = get_memory_index()
except Exception as e:
    memory = None
    _memory_error = str(e)


router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])


# ============================================================
# Internal helper — ensures memory is loaded
# ============================================================

def _ensure_memory_loaded():
    if memory is None:
        raise HTTPException(
            status_code=500,
            detail=f"Memory engine unavailable: {_memory_error}",
        )

    # 🔑 THIS IS THE KEY LINE (Option A)
    memory.ensure_loaded()


# ============================================================
# Routes
# ============================================================

@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    _ensure_memory_loaded()
    memory_id = memory.save_raw(payload)
    return {"status": "raw_saved", "memory_id": memory_id}


@router.post("/consolidate")
def memory_consolidate(user_id: Optional[str] = None):
    _ensure_memory_loaded()
    result = memory.consolidate(user_id=user_id)
    if not result:
        return {"status": "empty", "result": None}
    return {"status": "ok", "result": result}


@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    _ensure_memory_loaded()
    items = memory.list_recent(user_id=user_id, limit=limit)
    return {"count": len(items), "items": items}


@router.post("/system")
def memory_system(payload: Dict[str, Any]):
    _ensure_memory_loaded()
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
    _ensure_memory_loaded()
    return memory.build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
        include_global_fallback=include_global_fallback,
    )
