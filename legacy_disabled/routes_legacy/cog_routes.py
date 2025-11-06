from fastapi import APIRouter, Body

router = APIRouter(prefix="/cog", tags=["cog"])

@router.post("/reflect", summary="Store reflection about an action execution")
def reflect(payload: dict = Body(...)):
    return {"status": "ok", "received": payload}

@router.post("/score", summary="Store runtime scores/metrics")
def score(payload: dict = Body(...)):
    return {"status": "ok", "received": payload}

@router.get("/suggest", summary="Heuristic suggestions from recent meta")
def suggest():
    return {"status": "ok", "suggestions": []}
