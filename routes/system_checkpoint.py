from fastapi import APIRouter
from ops.system.checkpoint import create_checkpoint

router = APIRouter(prefix="/system", tags=["system"])

@router.post("/checkpoint")
def system_checkpoint(label: str = "manual"):
    create_checkpoint(label)
    return {"status": "ok", "label": label}
