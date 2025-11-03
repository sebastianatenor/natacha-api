from fastapi import APIRouter, Body, Query, HTTPException
from fastapi.responses import PlainTextResponse
import logging, traceback
from datetime import datetime, timezone
from typing import Optional

from google.cloud import firestore
from app.utils.firestore_client import get_client

router = APIRouter(tags=["tasks"])
logger = logging.getLogger("tasks")


@router.get("/tasks/search")
def task_search(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    """Busca tareas; ordena por timestamp (fallback created_at) y filtra opcionalmente por project/state."""
    db = get_client()
    try:
        q = db.collection("assistant_tasks").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        )
    except Exception:
        q = db.collection("assistant_tasks").order_by(
            "created_at", direction=firestore.Query.DESCENDING
        )

    docs = q.limit(200).stream()
    out = []
    for d in docs:
        item = d.to_dict()
        if project and item.get("project") != project:
            continue
        if state and item.get("state") != state:
            continue
        out.append({"id": d.id, **item})
        if len(out) >= limit:
            break
    return out


@router.post("/tasks/add")
def task_add(payload: dict = Body(...)):
    """Inserta una tarea con validación mínima y timestamps ISO-UTC."""
    try:
        req = {k: payload.get(k, "") for k in ("summary","detail","project","channel","state","visibility","impact")}
        # campos requeridos
        for k in ("summary","project","channel"):
            if not req[k]:
                raise HTTPException(status_code=400, detail=f"{k} is required")

        now = datetime.now(timezone.utc).isoformat()
        doc = {
            **req,
            "state": req.get("state") or "vigente",
            "visibility": req.get("visibility") or "equipo",
            "impact": req.get("impact") or "medio",
            "timestamp": now,
            "created_at": now,
            "created_by": "api.tasks.add",
        }
        db = get_client()
        db.collection("assistant_tasks").add(doc)
        return {"status": "ok", "stored": doc}
    except HTTPException:
        raise
    except Exception:
        tb = traceback.format_exc()
        logger.exception("tasks.add failed | payload=%s\n%s", payload, tb)
        return PlainTextResponse(tb, status_code=500)


# Endpoints diagnósticos (para aislar problemas de ruteo/Firestore)
@router.post("/tasks/add_raw")
def tasks_add_raw(payload: dict = Body(...)):
    """Inserción permisiva sin validaciones — útil para aislar errores."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "summary": payload.get("summary", "no-summary"),
            "detail": payload.get("detail", ""),
            "project": payload.get("project", "LLVC"),
            "channel": payload.get("channel", "gpt-chat"),
            "state": payload.get("state", "vigente"),
            "visibility": payload.get("visibility", "equipo"),
            "impact": payload.get("impact", "medio"),
            "timestamp": now,
            "created_at": now,
            "created_by": "api.tasks.add_raw",
        }
        db = get_client()
        db.collection("assistant_tasks").add(doc)
        return {"status":"ok","stored":doc}
    except Exception:
        return PlainTextResponse(traceback.format_exc(), status_code=500)


@router.get("/tasks/selftest")
def tasks_selftest():
    """Autotest: escribe un doc mínimo en assistant_tasks y devuelve 200 si todo ok."""
    try:
        now = datetime.now(timezone.utc).isoformat()
        doc = {
            "summary": "tasks.selftest",
            "detail": "autotest",
            "project": "LLVC",
            "channel": "selftest",
            "state": "vigente",
            "visibility": "equipo",
            "impact": "bajo",
            "timestamp": now,
            "created_at": now,
            "created_by": "api.tasks.selftest",
        }
        db = get_client()
        db.collection("assistant_tasks").add(doc)
        return {"status":"ok","wrote":"assistant_tasks","doc":doc}
    except Exception:
        return PlainTextResponse(traceback.format_exc(), status_code=500)
