import os
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query
from google.cloud import firestore
from google.oauth2 import service_account
from google.api_core.exceptions import FailedPrecondition

router = APIRouter(tags=["memory"])

# Proyecto por defecto (tu Cloud Run actual)
PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")


def get_db():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "firestore-key.json")
    if cred_path and os.path.exists(cred_path):
        creds = service_account.Credentials.from_service_account_file(cred_path)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    return firestore.Client(project=PROJECT_ID)


# Palabras que disparan “esto parece una tarea”
TRIGGER_WORDS = [
    "enviar",
    "mandar",
    "llamar",
    "preparar",
    "revisar",
    "pasar",
    "cotizar",
    "seguir",
    "recordar",
    "contactar",
    "avisar",
    "confirmar",
    "pagar",
    "armar",
]


def looks_like_task(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(word in lower for word in TRIGGER_WORDS)


def recent_task_exists(db, title: str, project: str) -> bool:
    """
    Evita duplicados obvios: si en los últimos 5 minutos se creó
    una tarea con el mismo título y proyecto, no la vuelve a crear.
    """
    five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    q = (
        db.collection("assistant_tasks")
        .where("project", "==", project)
        .where("title", "==", title[:100])
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(3)
    )

    try:
        docs = list(q.stream())
    except Exception:
        # si Firestore no soporta el order_by+where así en tu modo, salimos sin bloquear
        return False

    for d in docs:
        data = d.to_dict()
        created_at = data.get("created_at")
        try:
            if created_at and created_at >= five_minutes_ago.isoformat():
                return True
        except Exception:
            # si el formato no es ISO estricta, lo ignoramos
            continue
    return False


def create_task_from_memory(db, memory_doc: dict):
    """Crea una tarea y registra una memoria de que la creó."""
    summary = memory_doc.get("summary", "")
    if not looks_like_task(summary):
        return  # no parece tarea, salimos

    project = memory_doc.get("project", "general")

    # evitar duplicados inmediatos
    if recent_task_exists(db, summary, project):
        return

    # 1) crear la tarea
    task = {
        "title": summary[:100],
        "detail": memory_doc.get("detail", ""),
        "project": project,
        "channel": memory_doc.get("channel", "memory-auto"),
        "state": "pending",
        "due": "",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "visibility": memory_doc.get("visibility", "equipo"),
        "created_by": memory_doc.get("created_by", "memory.auto"),
    }
    task_ref = db.collection("assistant_tasks").add(task)

    # 2) registrar que la creó (auto-loop de conciencia)
    confirm_memory = {
        "summary": f"Tarea creada automáticamente: {task['title']}",
        "detail": f"Origen: memoria.add | task_id: {task_ref[1].id}",
        "channel": "system-auto",
        "project": project,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "state": "vigente",
        "visibility": "equipo",
        "impact": "medio",
    }
    db.collection("assistant_memory").add(confirm_memory)


@router.post("/memory/add")
def memory_add(payload: dict):
    db = get_db()

    summary = (payload.get("summary") or "").strip()
    if not summary:
        raise HTTPException(status_code=400, detail="summary is required")

    now_iso = datetime.now(timezone.utc).isoformat()

    doc = {
        "summary": summary,
        "detail": payload.get("detail", ""),
        "channel": payload.get("channel", "unknown"),
        "project": payload.get("project", "general"),
        "timestamp": now_iso,
        "state": payload.get("state", "vigente"),
        # extras
        "visibility": payload.get("visibility", "equipo"),
        "created_by": payload.get("created_by", "api.memory.add"),
    }

    # opcional: links de origen
    source_links = payload.get("source_links") or payload.get("links")
    if source_links:
        # lo dejamos siempre como lista
        if isinstance(source_links, str):
            source_links = [source_links]
        doc["source_links"] = source_links

    # guardo la memoria original
    try:
        db.collection("assistant_memory").add(doc)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Firestore error (create memory): {e!r}"
        )

    # si parece tarea → creo tarea + anoto que la creé
    try:
        create_task_from_memory(db, doc)
    except Exception as e:
        # no rompemos la respuesta si falló el auto-task
        return {
            "status": "ok",
            "stored": doc,
            "warning": f"task not created: {e!r}",
        }

    return {"status": "ok", "stored": doc}


@router.get("/memory/search", tags=["memory"])
def memory_search(
    project: str = Query(default=None),
    channel: str = Query(default=None),
    query: str = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    db = get_db()
    col = db.collection("assistant_memory")

    def _post_filter(items):
        # filtro en memoria por texto si viene query
        if query:
            q_lower = query.lower()
            items = [
                it for it in items
                if q_lower in ((it.get("summary") or "") + " " + (it.get("detail") or "")).lower()
            ]
        return items[:limit]

    # --- Intento A: filtros directos en Firestore ---
    try:
        if project or channel:
            q = col
            if project:
                q = q.where("project", "==", project)
            if channel:
                q = q.where("channel", "==", channel)
            docs = q.limit(200).stream()

            results = []
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                results.append(data)
            return _post_filter(results)

        # sin filtros → más nuevos por timestamp
        q = col.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(200)
        docs = q.stream()
        results = []
        for d in docs:
            data = d.to_dict()
            data["id"] = d.id
            results.append(data)
        return _post_filter(results)

    except Exception as e:
        # --- Intento B (fallback): traer recientes y filtrar en memoria ---
        q = col.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(200)
        docs = q.stream()
        results = []
        for d in docs:
            data = d.to_dict()
            data["id"] = d.id
            results.append(data)

        # aplicar filtros en memoria si vinieron
        if project:
            results = [r for r in results if (r.get("project") or "") == project]
        if channel:
            results = [r for r in results if (r.get("channel") or "") == channel]

        return _post_filter(results)


@router.get("/memory/search", tags=["memory"])
def memory_search_safe(
    project: str = Query(default=None),
    channel: str = Query(default=None),
    query: str = Query(default=None),
    limit: int = Query(default=20, le=100),
):
    """
    Versión con fallback: si Firestore pide índice, traemos últimos por timestamp
    y filtramos en memoria para evitar 500.
    """
    db = get_db()
    col = db.collection("assistant_memory")

    def _stream_latest():
        q2 = col.order_by("timestamp", direction=firestore.Query.DESCENDING)
        return q2.limit(min(200, max(20, limit))).stream()

    try:
        if project or channel:
            q = col
            if project:
                q = q.where("project", "==", project)
            if channel:
                q = q.where("channel", "==", channel)
            docs = q.limit(min(200, max(20, limit))).stream()

            results = []
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                results.append(data)
        else:
            docs = _stream_latest()
            results = []
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                results.append(data)

    except FailedPrecondition:
        # 🔁 Fallback: falta índice → traemos últimos y filtramos en memoria
        results = []
        for d in _stream_latest():
            data = d.to_dict()
            data["id"] = d.id
            results.append(data)
        if project:
            results = [x for x in results if (x.get("project") or "") == project]
        if channel:
            results = [x for x in results if (x.get("channel") or "") == channel]

    # Filtro por texto opcional
    if query:
        q_lower = query.lower()
        results = [
            x for x in results
            if q_lower in ((x.get("summary") or "") + " " + (x.get("detail") or "")).lower()
        ]

    return results[:limit]
