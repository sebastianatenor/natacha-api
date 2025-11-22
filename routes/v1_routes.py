from typing import Optional, Dict, Any
from fastapi import APIRouter, Body, Query
import requests
import os

router = APIRouter(prefix="/v1", tags=["v1"])

# Detecta BASE del propio servicio
BASE = os.getenv("BASE_URL", "").strip()
if not BASE:
    BASE = "http://localhost:8000"

# -----------------------------
# 1) /v1/tasks/add  → proxy real
# -----------------------------
@router.post("/tasks/add")
def v1_tasks_add(payload: Dict[str, Any] = Body(...)):
    url = f"{BASE}/tasks/add"
    r = requests.post(url, json=payload, timeout=10)
    return {
        "status": "ok",
        "source": "v1_proxy_add",
        "item": r.json().get("item"),
    }

# -----------------------------
# 2) /v1/tasks/search  → proxy real
# -----------------------------
@router.get("/tasks/search")
def v1_tasks_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20),
):
    params = {
        "project": project,
        "state": state,
        "limit": limit,
    }
    url = f"{BASE}/tasks/list"
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    return {
        "status": "ok",
        "source": "v1_proxy_search",
        "items": data.get("items", []),
    }

# -----------------------------
# 3) /v1/tasks/update  → proxy REAL nuevo
# -----------------------------
@router.post("/tasks/update")
def v1_tasks_update(payload: Dict[str, Any] = Body(...)):
    """
    Proxy real: reenviamos a /tasks/update
    """
    url = f"{BASE}/tasks/update"
    r = requests.post(url, json=payload, timeout=10)
    out = r.json()

    return {
        "status": "ok",
        "source": "v1_proxy_update",
        "item": out.get("item"),
    }
