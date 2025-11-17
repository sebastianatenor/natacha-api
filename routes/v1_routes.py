from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional
from datetime import datetime, timezone

from routes.memory_routes import get_db as _get_db
from routes.tasks_routes import tasks_add as _tasks_add, tasks_list as _tasks_search, tasks_update as _tasks_update

router = APIRouter(prefix="/v1", tags=["v1"])

# ---------------------------
# /v1/tasks/add
# ---------------------------
@router.post("/v1/tasks/add")
async def v1_tasks_add(payload: dict = Body(...)):
    """
    Proxy async-safe hacia routes.tasks_routes.tasks_add
    """
    try:
        # ⚡ Aseguramos await
        result = await _tasks_add(payload)
        return {"status": "ok", "task": result}
    except Exception as e:
        print("[ERROR] v1_tasks_add ->", e)
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------
# /v1/tasks/search
# ---------------------------
@router.get("/v1/tasks/search")
async def v1_tasks_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
):
    res = await _tasks_search(project=project, state=state, limit=limit)
    return {"status": "ok", "data": res}

# ---------------------------
# /v1/tasks/update
# ---------------------------
@router.post("/v1/tasks/update")
async def v1_tasks_update(payload: dict = Body(...)):
    res = await _tasks_update(payload)
    return {"status": "ok", "data": res}
