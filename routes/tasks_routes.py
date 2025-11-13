from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from google.cloud import firestore


router = APIRouter()  # sin prefix, paths planos: /tasks/add, /tasks/list, /tasks/update


# =========================
#  Modelos Pydantic
# =========================

class TaskBase(BaseModel):
    user_id: str
    title: str = ""
    detail: str = ""
    project: str = ""
    channel: str = ""
    due: str = ""
    state: str = "pending"
    evidence: List[Dict[str, Any]] = Field(default_factory=list)


class TaskCreate(TaskBase):
    """Payload de creación de tareas."""
    pass


class TaskUpdate(BaseModel):
    user_id: str
    task_id: str
    title: Optional[str] = None
    detail: Optional[str] = None
    project: Optional[str] = None
    channel: Optional[str] = None
    due: Optional[str] = None
    state: Optional[str] = None
    evidence: Optional[List[Dict[str, Any]]] = None


def _get_db() -> firestore.Client:
    """Cliente Firestore compartido."""
    return firestore.Client()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# =========================
#  /tasks/add
# =========================

@router.post("/tasks/add")
async def tasks_add(payload: TaskCreate) -> Dict[str, Any]:
    """
    Crea una tarea simple en la colección 'tasks'.

    Importante: NO usa consultas 'in' ni listas vacías,
    así evitamos errores tipo "'values' must be non-empty".
    """
    db = _get_db()
    col = db.collection("tasks")

    now = _now_iso()
    doc_ref = col.document()  # ID auto
    task_id = doc_ref.id

    safe_project = payload.project or ""
    safe_title = payload.title or ""
    # Clave opaca, no dependemos de formato viejo
    key = f"{safe_project}:{safe_title}:{task_id}"

    doc: Dict[str, Any] = {
        "user_id": payload.user_id,
        "title": payload.title,
        "detail": payload.detail,
        "project": payload.project,
        "channel": payload.channel,
        "due": payload.due or "",
        "state": payload.state or "pending",
        "evidence": payload.evidence or [],
        "created_at": now,
        "updated_at": now,
        "source": "tasks_routes",
        "key": key,
    }

    doc_ref.set(doc)
    doc["id"] = task_id
    return doc


# =========================
#  /tasks/list
# =========================

@router.get("/tasks/list")
async def tasks_list(
    user_id: Optional[str] = Query(default=None),
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
) -> Dict[str, Any]:
    """
    Lista tareas desde Firestore.

    Filtros opcionales:
    - user_id
    - project
    - state
    """
    db = _get_db()
    col = db.collection("tasks")

    query = col
    if user_id:
        query = query.where("user_id", "==", user_id)
    if project:
        query = query.where("project", "==", project)
    if state:
        query = query.where("state", "==", state)

    docs = list(query.stream())
    items: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict() or {}
        data["id"] = d.id
        items.append(data)

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
    }


# =========================
#  /tasks/update
# =========================

@router.post("/tasks/update")
async def tasks_update(payload: TaskUpdate) -> Dict[str, Any]:
    """
    Actualiza campos de una tarea existente.
    - Requiere: user_id, task_id
    - Campos opcionales: title, detail, project, channel, due, state, evidence
    """
    db = _get_db()
    col = db.collection("tasks")

    if not payload.task_id:
        raise HTTPException(status_code=400, detail="missing id")

    doc_ref = col.document(payload.task_id)
    snap = doc_ref.get()
    if not snap.exists:
        raise HTTPException(status_code=404, detail="task not found")

    current = snap.to_dict() or {}

    update_data: Dict[str, Any] = {}
    for field in ["title", "detail", "project", "channel", "due", "state", "evidence"]:
        value = getattr(payload, field)
        if value is not None:
            update_data[field] = value

    if not update_data:
        # Nada que actualizar: devolvemos el estado actual
        current["id"] = payload.task_id
        return current

    update_data["updated_at"] = _now_iso()
    doc_ref.update(update_data)

    current.update(update_data)
    current["id"] = payload.task_id
    return current
