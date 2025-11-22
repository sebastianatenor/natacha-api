from typing import Optional, Dict, Any

from fastapi import APIRouter, Body, Query

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/tasks/add")
def v1_tasks_add(payload: Dict[str, Any] = Body(...)):
    """
    Stub v1: simplemente devuelve lo que recibió.
    (Sin Firestore, sin lógica interna)
    """
    return {
        "status": "ok",
        "source": "v1_stub_add",
        "received": payload,
    }


@router.get("/tasks/search")
def v1_tasks_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
):
    """
    Stub v1: devuelve una lista vacía, solo para probar que la ruta funciona.
    """
    return {
        "status": "ok",
        "source": "v1_stub_search",
        "project": project,
        "state": state,
        "limit": limit,
        "items": [],
    }


@router.post("/tasks/update")
def v1_tasks_update(payload: Dict[str, Any] = Body(...)):
    """
    Stub v1: devuelve el payload como está.
    """
    return {
        "status": "ok",
        "source": "v1_stub_update",
        "received": payload,
    }
