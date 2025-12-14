from fastapi import APIRouter, HTTPException
from unified_core.memory_snapshot import create_memory_snapshot

router = APIRouter(
    prefix="/ops/memory",
    tags=["memory-ops"],
)


@router.post("/snapshot")
def snapshot_memory():
    result = create_memory_snapshot()

    if result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=result)

    return result
