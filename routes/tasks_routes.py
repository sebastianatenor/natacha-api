from fastapi import APIRouter, Body, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from routes.memory_routes import get_db as _get_db

router = APIRouter()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

# =========================
#  /tasks/add
# =========================

@router.post("/tasks/add")
async def tasks_add(payload: dict = Body(...)) -> Dict[str, Any]:
    """
    Crea una tarea simple en la colección 'tasks'.

    Compatible con entorno síncrono (dev) y asíncrono (Cloud Run).
    """
    try:
        db = _get_db()
        col = db.collection("tasks")

        now = _now_iso()
        doc_ref = col.document()  # ID auto
        task_id = doc_ref.id

        safe_project = payload.get("project") or ""
        safe_title = payload.get("title") or ""
        key = f"{safe_project}:{safe_title}:{task_id}"

        doc: Dict[str, Any] = {
            "user_id": payload.get("user_id"),
            "title": payload.get("title"),
            "detail": payload.get("detail"),
            "project": payload.get("project"),
            "channel": payload.get("channel"),
            "due": payload.get("due") or "",
            "state": payload.get("state") or "pending",
            "evidence": payload.get("evidence") or [],
            "created_at": now,
            "updated_at": now,
            "source": "tasks_routes",
            "key": key,
        }

        # Si .set() es coroutine (modo async Firestore), hacemos await
        result = doc_ref.set(doc)
        if hasattr(result, "__await__"):
            await result

        doc["id"] = task_id
        return {"status": "ok", "task": doc}

    except Exception as e:
        return {"status": "error", "detail": str(e)}

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

    return {"status": "ok", "tasks": items}
