from fastapi import APIRouter

router = APIRouter(tags=["System"])

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/__alive")
def alive():
    return {"alive": True}

