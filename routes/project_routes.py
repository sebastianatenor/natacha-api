from fastapi import APIRouter, HTTPException
from natacha_core.project_memory import save_project, get_project, search_projects

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("/save")
async def project_save(payload: dict):
    project_id = payload.get("id")
    if not project_id:
        raise HTTPException(status_code=400, detail="Missing id")
    return save_project(project_id, payload)

@router.get("/get")
async def project_get(project_id: str):
    out = get_project(project_id)
    if not out:
        raise HTTPException(status_code=404, detail="Not found")
    return out

@router.get("/search")
async def project_search(limit: int = 20):
    return {"items": search_projects(limit=limit)}
