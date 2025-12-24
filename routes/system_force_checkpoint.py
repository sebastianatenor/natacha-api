# routes/system_force_checkpoint.py
from fastapi import APIRouter

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.post("/force_checkpoint")
def force_checkpoint(payload: dict):
    label = payload.get("label", "manual-checkpoint")

    from ops.system.checkpoint_writer import write_checkpoint

    return write_checkpoint(label)
