from typing import Optional, Dict, Any

from fastapi import APIRouter, Body, Query, HTTPException

# Importamos el core de tareas (Firestore)
from routes.tasks_routes import TaskCreate, TaskUpdate, tasks_add, tasks_list, tasks_update

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/tasks/add")
def v1_tasks_add(payload: Dict[str, Any] = Body(...)):
    """
    /v1/tasks/add
    Fachada estable:
    - Acepta payload flexible (viene de acciones / agentes)
    - Adapta al modelo TaskCreate
    - Delegamos en core /tasks/add (Firestore)
    """
    try:
        task = TaskCreate(
            user_id=payload.get("user_id") or payload.get("user") or "sebastian",
            title=payload.get("title") or payload.get("summary") or "untitled",
            detail=payload.get("detail") or payload.get("description") or "",
            project=payload.get("project") or "LLVC",
            channel=payload.get("channel") or "chatgpt",
            due=payload.get("due") or payload.get("due_at") or "",
            state=payload.get("state") or "pending",
            evidence=payload.get("evidence") or [],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"invalid payload: {e}")

    core_resp = tasks_add(task)  # llama al core /tasks/add
    item = core_resp.get("item") if isinstance(core_resp, dict) else None

    return {
        "status": "ok",
        "source": "v1_proxy_add",
        "item": item,
    }


@router.get("/tasks/search")
def v1_tasks_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
):
    """
    /v1/tasks/search
    Fachada estable:
    - Reutiliza core /tasks/list
    - Devuelve items completos como array simple
    """
    core_resp = tasks_list(
        user_id=None,
        project=project,
        state=state,
        limit=limit,
    )

    items = []
    if isinstance(core_resp, dict):
        items = core_resp.get("items") or []

    return {
        "status": "ok",
        "source": "v1_proxy_search",
        "project": project,
        "state": state,
        "limit": limit,
        "items": items,
    }


@router.post("/tasks/update")
def v1_tasks_update(payload: Dict[str, Any] = Body(...)):
    """
    /v1/tasks/update
    Fachada estable:
    - Requiere id
    - Campos opcionales: title, detail/description, state, due/due_at
    """
    task_id = payload.get("id")
    if not task_id:
        raise HTTPException(status_code=400, detail="field 'id' is required")

    upd = TaskUpdate(
        id=task_id,
        title=payload.get("title"),
        detail=payload.get("detail") or payload.get("description"),
        state=payload.get("state"),
        due=payload.get("due") or payload.get("due_at"),
    )

    core_resp = tasks_update(upd)
    item = core_resp.get("item") if isinstance(core_resp, dict) else None

    return {
        "status": "ok",
        "source": "v1_proxy_update",
        "item": item,
    }
