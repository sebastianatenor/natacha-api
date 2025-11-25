from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from google.cloud.firestore import Query as FireQuery
from google.cloud import firestore
from routes.db_util import get_client, get_db
from datetime import datetime, timezone
import logging, os, json, inspect, hashlib

router = APIRouter(tags=["ops"])
PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")

# === Snapshot manual ===
@router.post("/ops/snapshot")
def take_snapshot():
    db = get_db()
    if db is None:
        logging.error("ops_snapshot: backend Firestore no disponible")
        return JSONResponse({
            "status": "unavailable",
            "backend": "firestore",
            "hint": "ver credenciales/roles o variable OPS_DISABLE_FIRESTORE",
            "route": "ops_snapshot"
        }, status_code=503)

    memories_ref = db.collection("assistant_memory").limit(200)
    memories = [dict(doc.to_dict(), id=doc.id) for doc in memories_ref.stream()]

    tasks_ref = db.collection("assistant_tasks").limit(200)
    tasks = [dict(doc.to_dict(), id=doc.id) for doc in tasks_ref.stream()]

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
        "tasks_preview": _tasks_snapshot(get_client)
    }


@router.get("/ops/snapshots")
def list_snapshots(
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Cantidad máxima de snapshots a devolver (máx 50).",
    ),
    project: str | None = Query(
        None,
        description="Filtro de proyecto (por campo 'project' o por tag, ej. 'LLVC' o 'Natacha').",
    ),
    include_raw: bool = Query(
        False,
        description="Si es true, incluye el contenido crudo (raw/memories/tasks).",
    ),
):
    """
    Lista snapshots operativos en formato SLIM por defecto.

    - Por defecto devuelve solo metadata liviana:
      id, created_at, project, tags, kind, importance, source, user_id, note,
      total_memories y total_tasks.
    - Si include_raw=true, agrega el contenido crudo:
      - snapshots nuevos: campo 'raw'
      - snapshots manuales: 'memories' y 'tasks'
    """
    db = get_db()
    if db is None:
        return JSONResponse({"status": "unavailable"}, status_code=503)

    snaps_ref = (
        db.collection("assistant_snapshots")
        .order_by("created_at", direction=FireQuery.DESCENDING)
        .limit(limit)
    )
    raw_snaps = [dict(doc.to_dict(), id=doc.id) for doc in snaps_ref.stream()]

    # Filtro opcional por proyecto:
    # respeta tanto el campo 'project' como que el nombre del proyecto esté en 'tags'.
    if project:
        filtered = []
        for s in raw_snaps:
            proj = s.get("project")
            tags = s.get("tags") or []
            if proj == project or (isinstance(tags, list) and project in tags):
                filtered.append(s)
        raw_snaps = filtered

    items = []
    for s in raw_snaps:
        base = {
            "id": s.get("id"),
            "created_at": s.get("created_at"),
            "project": s.get("project"),
            "tags": s.get("tags", []),
            "kind": s.get("kind"),
            "importance": s.get("importance"),
            "source": s.get("source"),
            "user_id": s.get("user_id"),
            "note": s.get("note"),
            # Para snapshots manuales tipo /ops/snapshot:
            "total_memories": s.get("total_memories"),
            "total_tasks": s.get("total_tasks"),
        }

        # Solo incluimos contenido pesado si lo pedís explícitamente
        if include_raw:
            if "raw" in s:
                # snapshots del motor de memoria (schema nuevo)
                base["raw"] = s.get("raw")
            else:
                # snapshots manuales que tenían 'memories' y 'tasks' embebidos
                if "memories" in s:
                    base["memories"] = s.get("memories")
                if "tasks" in s:
                    base["tasks"] = s.get("tasks")

        # Limpiamos claves None para que la respuesta quede prolija
        compact = {k: v for k, v in base.items() if v is not None}
        items.append(compact)

    return {
        "count": len(items),
        "items": items,
    }


@router.get("/ops/summary")
def ops_summary(limit: int = 10):
    db = get_db()
    if db is None:
        return JSONResponse({"status": "unavailable"}, status_code=503)

    mem_docs = db.collection("assistant_memory").order_by("timestamp", direction=FireQuery.DESCENDING).limit(limit).stream()
    memories = [dict(d.to_dict(), id=d.id) for d in mem_docs]

    task_docs = db.collection("assistant_tasks").order_by("created_at", direction=FireQuery.DESCENDING).limit(limit).stream()
    tasks = [dict(d.to_dict(), id=d.id) for d in task_docs]

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
    db = get_db()
    if db is None:
        return JSONResponse({"status": "unavailable"}, status_code=503)

    mem_docs = db.collection("assistant_memory").order_by("timestamp", direction=FireQuery.DESCENDING).limit(limit).stream()
    memories = [dict(d.to_dict(), id=d.id) for d in mem_docs]

    task_docs = db.collection("assistant_tasks").order_by("created_at", direction=FireQuery.DESCENDING).limit(limit).stream()
    tasks = [dict(d.to_dict(), id=d.id) for d in task_docs]

    by_project = {}
    for m in memories:
        p = m.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["memories"].append(m)
    for t in tasks:
        p = t.get("project", "general")
        by_project.setdefault(p, {"memories": [], "tasks": []})
        by_project[p]["tasks"].append(t)

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
    this_file = inspect.getsourcefile(ops_debug_source) or "<unknown>"
    with open(__file__, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    return {"file_runtime": this_file, "sha256_this_module": sha}


@router.post("/ops/self_register")
async def self_register(request: Request):
    """
    Persiste metadatos de runtime en /app/RUNTIME.json
    tomando datos del payload o, si faltan, de variables de entorno.
    """
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    rt = payload.get("runtime") or {}

    url = payload.get("url") or os.getenv("SERVICE_URL")
    if not url:
        try:
            url = str(getattr(request, "base_url", "")).rstrip("/")
        except Exception:
            url = ""

    runtime = {
        "primary": rt.get("primary") or "cloud_run",
        "legacy": rt.get("legacy") or "",
        "url": url,
        "region": os.getenv("REGION", "us-central1"),
        "revision": os.getenv("K_REVISION", "unknown"),
    }

    data = {
        "service": "natacha-api",
        "ts": datetime.now(timezone.utc).isoformat(),
        "runtime": runtime,
    }

    with open("/app/RUNTIME.json", "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "ok", "saved": "RUNTIME.json", "data": data}


def _tasks_snapshot(get_client, limit: int = 3):
    try:
        db = get_client()
        q = db.collection("assistant_tasks").order_by("created_at", direction="DESCENDING")
        items = []
        for i, doc in enumerate(q.stream()):
            if i >= limit:
                break
            d = doc.to_dict()
            d["id"] = doc.id
            items.append({
                "id": d.get("id", ""),
                "title": d.get("title", ""),
                "state": d.get("state", ""),
                "created_at": d.get("created_at", "")
            })
        return {"count": len(items), "items": items}
    except Exception as e:
        return {"error": str(e)}
