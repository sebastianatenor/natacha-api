from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from natacha_core import semantic_memory_v2

router = APIRouter(
    prefix="/memory/v2/semantic",
    tags=["memory_v2_semantic"],
)


class SemanticAddPayload(BaseModel):
    user_id: str
    project: str
    text: str
    tags: Optional[List[str]] = None
    people: Optional[List[str]] = None


@router.post("/add")
def semantic_add(payload: SemanticAddPayload):
    return semantic_memory_v2.save_event(
        user_id=payload.user_id,
        project=payload.project,
        text=payload.text,
        tags=payload.tags or [],
        people=payload.people or [],
    )


@router.get("/search")
def semantic_search(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
):
    items = semantic_memory_v2.search(
        user_id=user_id,
        project=project,
        q=q,
        limit=limit,
    )
    return {"items": items}


@router.get("/summary")
def semantic_summary(
    user_id: str,
    project: str,
    q: str,
    limit: int = 20,
):
    """
    Devuelve un resumen de los recuerdos más relevantes para la query dada.
    """
    return semantic_memory_v2.summarize(
        user_id=user_id,
        project=project,
        q=q,
        limit=limit,
    )
