import os
from datetime import datetime, timezone

from fastapi import APIRouter
from google.oauth2 import service_account

from app.utils.firestore_client import get_firestore_client

router = APIRouter(tags=["ops"])

PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")


def get_db():
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if cred_path and os.path.exists(cred_path):
        creds = service_account.Credentials.from_service_account_file(cred_path)
        return firestore.Client(project=PROJECT_ID, credentials=creds)
    return get_firestore_client()


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
        .order_by("created_at", direction=firestore.Query.DESCENDING)
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
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
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
        .order_by("created_at", direction=firestore.Query.DESCENDING)
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


# === capa de inteligencia ligera ===
@router.get("/ops/insights")
def ops_insights(limit: int = 20):
    """
    Igual que /ops/summary pero enriquecido:
    - agrupa por proyecto
    - detecta tareas sin fecha
    - marca la más urgente
    - detecta títulos duplicados
    """
    db = get_db()

    # traer memorias
    mem_docs = (
        db.collection("assistant_memory")
        .order_by("timestamp", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    memories = [dict(d.to_dict(), id=d.id) for d in mem_docs]

    # traer tareas
    task_docs = (
        db.collection("assistant_tasks")
        .order_by("created_at", direction=firestore.Query.DESCENDING)
        .limit(limit)
        .stream()
    )
    tasks = [dict(d.to_dict(), id=d.id) for d in task_docs]

    # agrupar por proyecto
    by_project = {}
    for m in memories:
        p = m.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["memories"].append(m)

    for t in tasks:
        p = t.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["tasks"].append(t)

    # detectar duplicados por título
    title_index = {}
    for t in tasks:
        title = (t.get("title") or "").strip().lower()
        if not title:
            continue
        title_index.setdefault(title, []).append(t)

    duplicates = []
    for title, items in title_index.items():
        if len(items) > 1:
            duplicates.append(
                {
                    "title": title,
                    "count": len(items),
                    "ids": [i["id"] for i in items],
                }
            )

    # armar salida por proyecto
    projects_out = []
    for name, data in by_project.items():
        pending_tasks = [
            t for t in data["tasks"] if t.get("state") in (None, "", "pending")
        ]
        # tarea más urgente
        dated = [t for t in pending_tasks if t.get("due")]
        if dated:
            urgent = sorted(dated, key=lambda x: x["due"])[0]
        else:
            urgent = pending_tasks[0] if pending_tasks else None

        alerts = []
        if dated:
            alerts.append(f"{len(dated)} tarea(s) con fecha")
        no_due = [t for t in pending_tasks if not t.get("due")]
        if no_due:
            alerts.append(f"{len(no_due)} tarea(s) sin fecha")

        projects_out.append(
            {
                "name": name,
                "pending_tasks": len(pending_tasks),
                "urgent_task": urgent,
                "recent_memory": data["memories"][0] if data["memories"] else None,
                "alerts": alerts,
            }
        )

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "projects": projects_out,
        "duplicates": duplicates,
        "raw": {"memories": len(memories), "tasks": len(tasks)},
    }
