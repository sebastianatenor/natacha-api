from datetime import datetime, timezone
from typing import Optional, List, Any

from fastapi import APIRouter, Body, HTTPException, Query
from pydantic import BaseModel, Field

from routes.db_util import get_client  # mismo helper que usan otros módulos

router = APIRouter(prefix="/tasks", tags=["tasks"])

COLLECTION = "assistant_tasks"


class TaskCreate(BaseModel):
    user_id: str
    title: str
    detail: str = ""
    project: str = "general"
    channel: str = "chatgpt"
    due: str = ""
    state: str = "pending"
    evidence: List[Any] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    id: str
    title: Optional[str] = None
    detail: Optional[str] = None
    state: Optional[str] = None
    due: Optional[str] = None


def _col():
    db = get_client()
    return db.collection(COLLECTION)


@router.post("/add")
def tasks_add(task: TaskCreate = Body(...)):
    """
    Core /tasks/add – crea una tarea en assistant_tasks.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    data = {
        "user_id": task.user_id,
        "title": task.title,
        "detail": task.detail,
        "project": task.project,
        "channel": task.channel,
        "due": task.due,
        "state": task.state,
        "evidence": task.evidence,
        "created_at": now_iso,
        "updated_at": now_iso,
    }

    col = _col()
    doc_ref = col.document()
    doc_ref.set(data)
    data["id"] = doc_ref.id

    return {"status": "ok", "item": data}


@router.get("/list")
def tasks_list(
    user_id: Optional[str] = Query(default=None),
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
):
    """
    Core /tasks/list – lista tareas filtrando por proyecto/estado/user.
    """
    col = _col()
    q = col

    if user_id:
        q = q.where("user_id", "==", user_id)
    if project:
        q = q.where("project", "==", project)
    if state:
        q = q.where("state", "==", state)

    # created_at es string ISO, orden lexicográfico sirve bien
    try:
        from google.cloud import firestore  # type: ignore

        q = q.order_by("created_at", direction=firestore.Query.DESCENDING)
    except Exception:
        # si por algún motivo no podemos order_by, no rompemos
        pass

    docs = q.limit(limit).stream()

    items: List[Any] = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        items.append(data)

    return {"status": "ok", "count": len(items), "items": items}


@router.post("/update")
def tasks_update(payload: TaskUpdate = Body(...)):
    """
    Core /tasks/update – actualiza campos básicos de una tarea.
    """
    col = _col()
    doc_ref = col.document(payload.id)
    snap = doc_ref.get()

    if not snap.exists:
        raise HTTPException(status_code=404, detail="task not found")

    update_data = {}
    for field in ("title", "detail", "state", "due"):
        value = getattr(payload, field)
        if value is not None:
            update_data[field] = value

    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    if not update_data:
        return {"status": "ok", "item": {**snap.to_dict(), "id": payload.id}}

    doc_ref.update(update_data)
    new = doc_ref.get().to_dict()
    new["id"] = payload.id

    return {"status": "ok", "item": new}
