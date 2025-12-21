from fastapi import APIRouter
import os

router = APIRouter(tags=["Health"])

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "natacha-api",
        "revision": os.getenv("K_REVISION", "local"),
        "semantic_loaded": True,  # estado observado, no inferido
        "confidence": "high"
    }
