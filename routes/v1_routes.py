from typing import Optional, Dict, Any

from fastapi import APIRouter, Body, Query, HTTPException

# Importamos los modelos y handlers core de tasks
from routes.tasks_routes import (
    TaskCreate,
    TaskUpdate,
    tasks_add,
    tasks_list,
    tasks_update,
)

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/tasks/add")
def v1_tasks_add(payload: Dict[str, Any] = Body(...)):
    """
    /v1/tasks/add – fachada estable hacia el core /tasks/add.

    - Valida el payload con TaskCreate.
    - Llama directamente a tasks_add(...) del módulo core.
    - Devuelve un envoltorio con source="v1_proxy_add".
    """
    try:
        task = TaskCreate(**payload)
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"invalid task payload: {e}")

    core_resp = tasks_add(task)  # dict con {"status": "ok", "item": {...}} idealmente

    item = core_resp.get("item", core_resp) if isinstance(core_resp, dict) else core_resp

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
    /v1/tasks/search – fachada estable hacia el core /tasks/list.

    Usa:
      - user_id: None
      - project, state, limit como vienen del query.
    """
    core_resp = tasks_list(
        user_id=None,
        project=project,
        state=state,
        limit=limit,
    )

    items = core_resp.get("items", []) if isinstance(core_resp, dict) else core_resp

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
    /v1/tasks/update – fachada estable hacia el core /tasks/update.

    Requiere:
      - id
    Opcionales:
      - title, detail, state, due
    """
    try:
        upd = TaskUpdate(**payload)
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"invalid task update payload: {e}")

    core_resp = tasks_update(upd)  # dict con {"status": "ok", "item": {...}} idealmente

    item = core_resp.get("item", core_resp) if isinstance(core_resp, dict) else core_resp

    return {
        "status": "ok",
        "source": "v1_proxy_update",
        "item": item,
    }
