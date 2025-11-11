from google.cloud import firestore
from app.utils.task_dedupe import stable_key
from fastapi import APIRouter, Body, HTTPException, Query
from datetime import datetime, timezone
from typing import Optional

# reusamos el cliente Firestore del proyecto
from routes.db_util import get_client

router = APIRouter()  # mismo esquema que auto_routes (sin prefix para mantener paths planos)

def now_iso():
    return datetime.now(timezone.utc).isoformat()

@router.post("/tasks/add")
def tasks_add(payload: dict = Body(...)):
    """
    Crea/actualiza una tarea en Firestore con deduplicación por (project,title,paths).
    Si existe una tarea 'pending' o 'vigente' con la misma key, hace append único de 'evidence'.
    """
    try:
        db = get_client()
        project = payload.get("project") or "Natacha"
        title = payload.get("title") or "(untitled)"
        detail = payload.get("detail") or ""
        channel = payload.get("channel") or "api"
        state = payload.get("state") or "pending"
        due = payload.get("due") or ""
        user_id = payload.get("user_id") or "system"

        # paths opcionales para generar clave estable (puede venir como 'suspect_paths' o 'paths')
        suspect_paths = payload.get("suspect_paths") or payload.get("paths") or []
        if not isinstance(suspect_paths, list):
            suspect_paths = [str(suspect_paths)]

        # dedupe key estable (project + title + paths normalizados/ordenados)
        key = stable_key(project, title, suspect_paths)

        col = db.collection("assistant_tasks")

        # Buscar si existe abierta (pending/vigente) con la misma key
        q = (col.where("key", "==", key)
                .where("state", "in", ["pending", "vigente"])
                .limit(1))
        matches = list(q.stream())

        # Campos base del documento
        base_doc = {
            "title": title,
            "detail": detail,
            "project": project,
            "channel": channel,
            "state": state,
            "due": due,
            "user_id": user_id,
            "key": key,
            "updated_at": now_iso(),
        }

        if matches:
            # Ya existe una abierta → append único de evidencia
            doc_ref = matches[0].reference
            update_payload = {
                **base_doc,
                "evidence": firestore.ArrayUnion(sorted(set(suspect_paths))) if suspect_paths else firestore.ArrayUnion([]),
            }
            # Si querés preservar 'created_at' original, solo actualizamos campos mutables:
            update_payload.pop("title", None)  # opcional: evitar sobreescribir si no querés
            update_payload.pop("project", None)
            update_payload.pop("channel", None)
            update_payload.pop("user_id", None)
            update_payload.pop("key", None)

            # Evitar ArrayUnion vacío (Firestore lo permite, pero por prolijidad):
            if suspect_paths:
                doc_ref.update(update_payload)
            else:
                # sin nueva evidencia: solo marca updated_at/state/detail
                doc_ref.update({k: v for k, v in update_payload.items() if k != "evidence"})

            return {"status": "ok", "id": matches[0].id, "deduped": True}
        else:
            # No existe → crear nueva
            doc = {
                **base_doc,
                "created_at": now_iso(),
                "source": "tasks_routes",
                "evidence": sorted(set(suspect_paths)) if suspect_paths else [],
            }
            ref = col.add(doc)
            task_id = ref[1].id if isinstance(ref, tuple) and len(ref) == 2 else getattr(ref, "id", "")
            return {"status": "ok", "id": task_id, "deduped": False, "task": doc}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tasks_add error: {e}")

@router.get("/tasks/list")
def tasks_list(
    project: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
):
    """
    Lista tareas desde Firestore (assistant_tasks), con filtros simples.
    """
    try:
        db = get_client()
        q = db.collection("assistant_tasks").order_by("created_at", direction="DESCENDING")
        if project:
            q = q.where("project", "==", project)
        if state:
            q = q.where("state", "==", state)

        items = []
        for i, doc in enumerate(q.stream()):
            if i >= limit:
                break
            d = doc.to_dict()
            d["id"] = doc.id
            items.append(d)
        return {"status": "ok", "count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tasks_list error: {e}")

@router.post("/tasks/update")
def tasks_update(payload: dict = Body(...)):
    """
    Actualiza campos simples de una tarea: state, due, title, detail, project, channel.
    Requiere: id
    """
    try:
        tid = payload.get("id")
        if not tid:
            raise HTTPException(status_code=400, detail="missing id")
        db = get_client()
        ref = db.collection("assistant_tasks").document(tid)
        fields = {k: v for k, v in payload.items() if k in {"state","due","title","detail","project","channel"}}
        if not fields:
            return {"status":"noop","id":tid}
        ref.update(fields)
        return {"status":"ok","id":tid,"updated":sorted(fields.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tasks_update error: {e}")
