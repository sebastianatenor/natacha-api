# routes/system_baseline/router.py

from fastapi import APIRouter
from ops.system.baseline_provider import read_baseline

router = APIRouter(
    prefix="/ops/system",
    tags=["system-baseline"],
)


@router.get("/baseline")
def get_system_baseline():
    return {
        "status": "ok",
        "baseline": read_baseline(),
        "confidence": "high",
    }
