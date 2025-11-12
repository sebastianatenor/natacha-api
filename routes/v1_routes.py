from fastapi import APIRouter, Body, HTTPException, Query
from typing import Optional, List, Any
from datetime import datetime, timezone

# Reuse Firestore client y helpers existentes
from routes.memory_routes import get_db as _get_db, looks_like_task as _looks_like_task
from routes.tasks_routes import tasks_add as _tasks_add, tasks_list as _tasks_search, tasks_update as _tasks_update

router = APIRouter(prefix="/v1", tags=["v1"])

# ---------- MEMORY ----------
@router.post("/memory/add")
def v1_memory_add(payload: dict = Body(...)):
    db = _get_db()
    summary = (payload.get("summary") or "").strip()
    if not summary:
        raise HTTPException(status_code=400, detail="summary is required")

    doc = {
        "summary": summary,
        "detail": payload.get("detail", ""),
        "channel": payload.get("channel", "unknown"),
        "project": payload.get("project", "general"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": payload.get("state", "vigente"),
        "visibility": payload.get("visibility", "equipo"),
        "created_by": payload.get("created_by", "api.v1.memory.add"),
        "source_links": payload.get("source_links") or payload.get("links") or [],
    }
    if isinstance(doc["source_links"], str):
        doc["source_links"] = [doc["source_links"]]

    db.collection("assistant_memory").add(doc)

    # Evita auto-tarea por ahora: fachada simple y segura
    return {"status": "ok", "data": doc}

@router.get("/memory/search")
def v1_memory_search(
    project: Optional[str] = Query(default=None),
    channel: Optional[str] = Query(default=None),
    query: Optional[str]   = Query(default=None),
    limit: int             = Query(default=20, le=100),
):
    db = _get_db()
    col = db.collection("assistant_memory")

    # 👉 Sin order_by cuando hay filtros -> NO requiere índices compuestos
    if project or channel:
        q = col
        if project:
            q = q.where("project", "==", project)
        if channel:
            q = q.where("channel", "==", channel)
        docs = q.limit(200).stream()
    else:
        # sin filtros: aceptamos order_by por timestamp (suele existir índice single-field)
        docs = col.order_by("timestamp", direction=1).limit(200).stream()

    results: List[Any] = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        results.append(data)

    if query:
        ql = query.lower()
        results = [
            it for it in results
            if ql in ((it.get("summary") or "") + " " + (it.get("detail") or "")).lower()
        ]

    return {"status": "ok", "count": len(results[:limit]), "items": results[:limit]}

# ---------- TASKS (fachada a tus handlers actuales) ----------
@router.post("/tasks/add")
def v1_tasks_add(payload: dict = Body(...)):
    res = _tasks_add(payload)
    return {"status": "ok", "data": res}

@router.get("/tasks/search")
def v1_tasks_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str]   = Query(default=None),
    limit: int             = Query(default=20, ge=1, le=200),
):
    res = _tasks_search(project=project, state=state, limit=limit)
    return {"status": "ok", "data": res}

@router.post("/tasks/update")
def v1_tasks_update(payload: dict = Body(...)):
    res = _tasks_update(payload)
    return {"status": "ok", "data": res}
