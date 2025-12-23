from fastapi import APIRouter
from ops.system.perception_provider import read_system_perception

router = APIRouter(
    prefix="/ops/system",
    tags=["system"],
)

@router.get("/perception")
def system_perception():
    perception = read_system_perception()
    return {
        "status": "ok",
        "perception": perception,
        "confidence": "high",
    }
