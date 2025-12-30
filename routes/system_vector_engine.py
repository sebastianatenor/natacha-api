from fastapi import APIRouter

router = APIRouter()

@router.post("/system/vector/init")
def vector_init():
    return {
        "engine": "vector",
        "mode": "stub",
        "index": "active",
        "embeddings": "disabled",
        "ready_for_ml": True,
    }

@router.get("/system/vector/status")
def vector_status():
    return {
        "engine": "vector",
        "loaded": True,
        "mode": "stub",
        "embeddings": False,
        "search": False,
    }
