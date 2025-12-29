from fastapi import APIRouter
from ops.snapshots.writer import write_snapshot

router = APIRouter(prefix="/system", tags=["system"])

@router.post("/snapshot")
def snapshot(label: str = "manual"):
    return write_snapshot(label)
