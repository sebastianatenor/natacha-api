from fastapi import APIRouter
from ops.system.state_aggregator import compute_system_state

router = APIRouter(prefix="/system", tags=["system"])

@router.get("/state_snapshot")
def state_snapshot():
    return compute_system_state()
