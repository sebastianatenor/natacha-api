from fastapi import APIRouter, Body, HTTPException, Query
from datetime import datetime, timezone
from typing import Optional

# reusamos el cliente Firestore del proyecto
from routes.db_util import get_client

router = APIRouter()  # mismo esquema que auto_routes (sin prefix para mantener paths planos)

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

@router.post("/tasks/add")
def tasks_add(payload: dict = Body(...)):
    """
    Crea una tarea mínima en Firestore.
    Espera (sugerido, no obligatorio): title, detail, project, channel, state, due, user_id
    """
    try:
        db = get_client()
        doc = {
            "title": payload.get("title") or "(untitled)",
            "detail": payload.get("detail") or "",
            "project": payload.get("project") or "Natacha",
            "channel": payload.get("channel") or "api",
            "state": payload.get("state") or "pending",
            "due": payload.get("due") or "",
            "user_id": payload.get("user_id") or "system",
            "created_at": _now_iso(),
            "source": "tasks_routes",
        }
        ref = db.collection("assistant_tasks").add(doc)
        task_id = ref[1].id if isinstance(ref, tuple) and len(ref) == 2 else getattr(ref, "id", "")
        return {"status": "ok", "id": task_id, "task": doc}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tasks_add error: {e}")

@router.get("/tasks/list")
def tasks_list(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
):
    """
    Lista tareas desde Firestore (assistant_tasks), con filtros simples.
    """
    try:
        db = get_client()
        q = db.collection("assistant_tasks").order_by("created_at", direction="DESCENDING")
        if project:
            q = q.where("project", "==", project)
        if state:
            q = q.where("state", "==", state)

        items = []
        for i, doc in enumerate(q.stream()):
            if i >= limit:
                break
            d = doc.to_dict()
            d["id"] = doc.id
            items.append(d)
        return {"status": "ok", "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tasks_list error: {e}")
