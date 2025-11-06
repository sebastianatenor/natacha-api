import os
from fastapi import APIRouter
router = APIRouter(prefix="/ops", tags=["ops"])

@router.get("/health")
def health():
    return {"ok": True, "service": "natacha-api-a", "rev": os.getenv("K_REVISION","unknown")}
