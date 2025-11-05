from routes.db_util import get_client
from fastapi.responses import JSONResponse
from google.cloud.firestore import Query as FireQuery
from google.cloud import firestore

import os

try:
    from routes.db_util import get_db
except Exception:
    def _fallback_get_db():
        return None
    get_db = _fallback_get_db
from datetime import datetime, timezone

from fastapi import APIRouter
import logging
from google.oauth2 import service_account
router = APIRouter(tags=["ops"])

PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")

@router.post("/ops/snapshot")
def take_snapshot():
    """
    Toma un snapshot simple de assistant_memory y assistant_tasks
    y lo guarda en assistant_snapshots. No altera nada existente.
    """
    db = get_db()

    # 1. leer memorias
    memories_ref = db.collection("assistant_memory").limit(200)
    memories = []
    for doc in memories_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        memories.append(data)

    # 2. leer tareas
    tasks_ref = db.collection("assistant_tasks").limit(200)
    tasks = []
    for doc in tasks_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        tasks.append(data)

    snapshot_doc = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "project": "LLVC",
        "total_memories": len(memories),
        "total_tasks": len(tasks),
        "memories": memories,
        "tasks": tasks,
        "source": "cloud-run:manual",
    }

    db.collection("assistant_snapshots").add(snapshot_doc)

    return {
        "status": "ok",
        "message": "snapshot creado",
        "memories": len(memories),
        "tasks": len(tasks),
    
    'tasks': _tasks_snapshot(get_client),
}


@router.get("/ops/snapshots")
def list_snapshots(limit: int = 10):
    """
    Lista los últimos snapshots tomados por Natacha.
    Sirve para que el GPT pueda ver el estado histórico.
    """
    db = get_db()
    snaps_ref = (
        db.collection("assistant_snapshots")
        .order_by("created_at", direction=FireQuery.DESCENDING)
        .limit(limit)
    )
    snaps = []
    for doc in snaps_ref.stream():
        data = doc.to_dict()
        data["id"] = doc.id
        snaps.append(data)
    return snaps


# === resumen operativo rápido (único) ===
@router.get("/ops/summary")
def ops_summary(limit: int = 10):
    """
    Devuelve en una sola respuesta:
    - últimas memorias
    - últimas tareas
    - agrupadas por proyecto
    """
    db = get_db()

    # 1) últimas memorias
    mem_docs = (
        db.collection("assistant_memory")
        .order_by("timestamp", direction=FireQuery.DESCENDING)
        .limit(limit)
        .stream()
    )
    memories = []
    for d in mem_docs:
        data = d.to_dict()
        data["id"] = d.id
        memories.append(data)

    # 2) últimas tareas
    task_docs = (
        db.collection("assistant_tasks")
        .order_by("created_at", direction=FireQuery.DESCENDING)
        .limit(limit)
        .stream()
    )
    tasks = []
    for d in task_docs:
        data = d.to_dict()
        data["id"] = d.id
        tasks.append(data)

    # 3) agrupar por proyecto
    by_project = {}
    for m in memories:
        p = m.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["memories"].append(m)

    for t in tasks:
        p = t.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["tasks"].append(t)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limit": limit,
        "memories": memories,
        "tasks": tasks,
        "by_project": by_project,
    }
@router.get("/ops/insights")
def ops_insights(limit: int = 20):
    """
    Igual que /ops/summary pero con un paneo "enriquecido":
    - últimas memorias y tareas
    - agrupación por proyecto
    - conteos y flags útiles
    """
    db = get_db()

    # Memorias
    mem_docs = (
        db.collection("assistant_memory")
        .order_by("timestamp", direction=FireQuery.DESCENDING)
        .limit(limit)
        .stream()
    )
    memories = []
    for d in mem_docs:
        data = d.to_dict()
        data["id"] = d.id
        memories.append(data)

    # Tareas
    task_docs = (
        db.collection("assistant_tasks")
        .order_by("created_at", direction=FireQuery.DESCENDING)
        .limit(limit)
        .stream()
    )
    tasks = []
    for d in task_docs:
        data = d.to_dict()
        data["id"] = d.id
        tasks.append(data)

    # Agrupar por proyecto + flags simples
    by_project = {}
    for m in memories:
        p = m.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["memories"].append(m)

    for t in tasks:
        p = t.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["tasks"].append(t)

    # Métricas simples
    metrics = {
        "total_memories": len(memories),
        "total_tasks": len(tasks),
        "projects": {k: {"memories": len(v["memories"]), "tasks": len(v["tasks"])} for k, v in by_project.items()},
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limit": limit,
        "memories": memories,
        "tasks": tasks,
        "by_project": by_project,
        "metrics": metrics,
    }

@router.get("/ops/debug_source")
def ops_debug_source():
        # Ruta real del archivo importado en runtime
        this_file = inspect.getsourcefile(ops_debug_source) or "<unknown>"
        # Hash del archivo de esta build
        with open(__file__, "rb") as fh:
            content = fh.read()
        sha = hashlib.sha256(content).hexdigest()
        return {"file_runtime": this_file, "sha256_this_module": sha}


def _tasks_snapshot(get_client, limit: int = 3):
    try:
        db = get_client()
        q = db.collection("assistant_tasks").order_by("created_at", direction="DESCENDING")
        items = []
        for i, doc in enumerate(q.stream()):
            if i >= limit: break
            d = doc.to_dict(); d["id"] = doc.id
            items.append({"id": d.get("id",""), "title": d.get("title",""), "state": d.get("state",""), "created_at": d.get("created_at","")})
        return {"count": len(items), "items": items}
    except Exception as e:
        return {"error": str(e)}
