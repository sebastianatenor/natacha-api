from fastapi import APIRouter, HTTPException
from natacha_core.people_memory import save_profile, get_profile, search_profiles

router = APIRouter(prefix="/people", tags=["people"])

@router.post("/save")
async def people_save(payload: dict):
    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="Missing id")
    return save_profile(user_id, payload)

@router.get("/get")
async def people_get(user_id: str):
    out = get_profile(user_id)
    if not out:
        raise HTTPException(status_code=404, detail="Not found")
    return out

@router.get("/search")
async def people_search(limit: int = 20):
    return {"items": search_profiles(limit=limit)}
