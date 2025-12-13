from typing import Optional, Dict, Any
from fastapi import APIRouter, Query

from unified_core.memory_lazy import get_memory_index

router = APIRouter(prefix="/memory/memory/engine", tags=["memory-engine"])

memory = get_memory_index()


@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    items = memory.list_recent(user_id=user_id, limit=limit)
    return {"count": len(items), "items": items}


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
        include_global_fallback=True,
    )
