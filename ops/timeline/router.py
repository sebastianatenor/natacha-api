from fastapi import APIRouter
from ops.timeline.builder import build_timeline

router = APIRouter(prefix="/ops/system", tags=["Timeline"])

@router.get("/timeline")
def timeline():
    return build_timeline()
