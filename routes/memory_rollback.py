from fastapi import APIRouter, HTTPException, Query

from unified_core.memory_rollback import rollback_memory

router = APIRouter(
    prefix="/ops/memory",
    tags=["memory-ops"],
)


@router.post("/rollback")
def rollback(
    snapshot: str = Query(..., description="Nombre exacto del snapshot"),
):
    result = rollback_memory(snapshot)

    if result.get("status") != "ok":
        raise HTTPException(status_code=400, detail=result)

    return result
