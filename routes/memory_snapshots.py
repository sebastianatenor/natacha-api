from fastapi import APIRouter, HTTPException

from unified_core.memory_snapshots import list_memory_snapshots

router = APIRouter(
    prefix="/ops/memory",
    tags=["memory-ops"],
)

@router.get("/snapshots")
def snapshots():
    result = list_memory_snapshots()

    if result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=result)

    return result
