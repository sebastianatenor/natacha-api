from fastapi import APIRouter
from natacha_core.semantic_memory_v2 import save_event, search

router = APIRouter(prefix="/memory/v2/semantic", tags=["memory_v2_semantic"])

@router.post("/add")
def semantic_add(payload: dict):
    return save_event(
        user_id=payload.get("user_id", "sebastian"),
        project=payload.get("project", "general"),
        text=payload.get("text", ""),
        tags=payload.get("tags", []),
        people=payload.get("people", []),
    )

@router.get("/search")
def semantic_search(limit: int = 50):
    return {"items": search(limit=limit)}
