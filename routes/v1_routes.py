from fastapi import APIRouter, Body, Query, HTTPException
from typing import Optional

from routes.tasks_routes import _create_task

router = APIRouter(prefix="/v1", tags=["v1"])

@router.post("/v1/tasks/add")
async def v1_tasks_add(payload: dict = Body(...)):
    try:
        result = await _create_task(payload)
        return {"status": "ok", "task": result}
    except Exception as e:
        print("[ERROR] v1_tasks_add ->", e)
        raise HTTPException(status_code=500, detail=str(e))
