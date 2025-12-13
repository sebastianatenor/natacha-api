from typing import Optional, Dict, Any
from fastapi import APIRouter, Query

import unified_core.memory_lazy as memory_lazy

# --------------------------------------------------
# Router (DEBE IR PRIMERO)
# --------------------------------------------------
router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])

# --------------------------------------------------
# Lazy memory singleton
# --------------------------------------------------
memory = memory_lazy.get_memory_index()

# --------------------------------------------------
# Endpoints
# --------------------------------------------------
@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    items = memory.list_recent(user_id=user_id, limit=limit)
    return {
        "count": len(items),
        "items": items,
    }


@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    memory_id = memory.save_raw(payload)
    return {"status": "raw_saved", "memory_id": memory_id}


@router.post("/consolidate")
def memory_consolidate(user_id: Optional[str] = None):
    result = memory.consolidate(user_id=user_id)
    return {"status": "ok", "result": result}


@router.get("/context_bundle")
def memory_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = Query(20, ge=1, le=200),
):
    return memory.build_context_bundle(
        user_id=user_id,
        recent_limit=recent_limit,
    )


# --------------------------------------------------
# Debug endpoint (OPCIONAL pero seguro)
# --------------------------------------------------
@router.get("/_debug_methods")
def debug_methods():
    return {
        "methods": sorted(
            [m for m in dir(memory) if not m.startswith("_")]
        )
    }
