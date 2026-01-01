from fastapi import APIRouter
from ops.system.capabilities import COGNITIVE_CAPABILITIES

router = APIRouter(prefix="/system/capabilities", tags=["system"])

@router.get("")
def get_capabilities():
    return {
        "status": "ok",
        "capabilities": COGNITIVE_CAPABILITIES
    }
