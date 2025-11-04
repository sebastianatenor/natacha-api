from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from google.cloud.firestore import Query as FireQuery
from routes.db_util import get_db
import os

router = APIRouter(tags=["ops"])
PROJECT_ID = os.getenv("GCP_PROJECT", "asistente-sebastian")

@router.get("/ops/ping")
def ops_ping():
    return {"ok": True, "component": "ops"}

@router.post("/ops/snapshot")
def take_snapshot():
    try:
        db = get_db()
        memories = []
        for doc in db.collection("assistant_memory").limit(200).stream():
            d = doc.to_dict(); d["id"] = doc.id; memories.append(d)

        tasks = []
        for doc in db.collection("assistant_tasks").limit(200).stream():
            d = doc.to_dict(); d["id"] = doc.id; tasks.append(d)

        snap = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "project": "LLVC",
            "total_memories": len(memories),
            "total_tasks": len(tasks),
            "memories": memories,
            "tasks": tasks,
            "source": "cloud-run:manual",
        }
        db.collection("assistant_snapshots").add(snap)
        return {"status":"ok","message":"snapshot creado","memories":len(memories),"tasks":len(tasks)}
    except Exception as e:
        return JSONResponse(status_code=503, content={"error":"db_error","detail":str(e)})

@router.get("/ops/snapshots")
def list_snapshots(limit: int = 10):
    try:
        db = get_db()
        snaps_ref = (
            db.collection("assistant_snapshots")
            .order_by("created_at", direction=FireQuery.DESCENDING)
            .limit(limit)
        )
        out = []
        for doc in snaps_ref.stream():
            d = doc.to_dict(); d["id"] = doc.id; out.append(d)
        return out
    except Exception as e:
        return JSONResponse(status_code=503, content={"error":"db_error","detail":str(e)})

@router.get("/ops/summary")
def ops_summary(limit: int = 10):
    try:
        db = get_db()

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

        by_project = {}
        for m in memories:
            k = m.get("project") or "Unassigned"
            by_project.setdefault(k, {"memories": [], "tasks": []})
            by_project[k]["memories"].append(m)
        for t in tasks:
            k = t.get("project") or "Unassigned"
            by_project.setdefault(k, {"memories": [], "tasks": []})
            by_project[k]["tasks"].append(t)

        return {"status":"ok","memories":len(memories),"tasks":len(tasks),"by_project":by_project}
    except Exception as e:
        return JSONResponse(status_code=503, content={"status":"error","where":"/ops/summary","type":e.__class__.__name__,"msg":str(e)})

@router.get("/ops/insights")
def ops_insights(limit: int = 20):
    try:
        db = get_db()

        task_docs = (
            db.collection("assistant_tasks")
            .order_by("created_at", direction=FireQuery.DESCENDING)
            .limit(limit)
            .stream()
        )
        tasks = []
        for d in task_docs:
            data = d.to_dict(); data["id"]=d.id; tasks.append(data)

        # simple enrich
        without_date = [t for t in tasks if not t.get("due_at")]
        most_urgent = None
        dated = [t for t in tasks if t.get("due_at")]
        if dated:
            most_urgent = sorted(dated, key=lambda x: x.get("due_at"))[0]

        by_project = {}
        for t in tasks:
            k = t.get("project") or "Unassigned"
            by_project.setdefault(k, {"tasks": []})
            by_project[k]["tasks"].append(t)

        return {
            "status":"ok",
            "total_tasks": len(tasks),
            "without_date": len(without_date),
            "most_urgent": most_urgent,
            "by_project": by_project
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={"status":"error","where":"/ops/insights","type":e.__class__.__name__,"msg":str(e)})

@router.api_route("/ops/smart_health", methods=["GET","POST"])
def ops_smart_health():
    """Chequeo de salud con prueba real a Firestore (limit 1)."""
    from datetime import datetime
    from fastapi.responses import JSONResponse
    try:
        db = get_db()
        # ping a colecciones clave con limit(1)
        mem = db.collection("assistant_memory").limit(1).stream()
        tasks = db.collection("assistant_tasks").limit(1).stream()

        # materializar uno para forzar la llamada
        _m = next(mem, None)
        _t = next(tasks, None)

        return {
            "ok": True,
            "ts": datetime.utcnow().isoformat() + "Z",
            "memory_sample": bool(_m),
            "tasks_sample": bool(_t),
            "component": "ops",
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "ok": False,
                "error": "db_error",
                "detail": str(e),
                "component": "ops",
            },
        )

@router.get("/ops/version")
def ops_version():
    # Requiere: from datetime import datetime, timezone (ya está importado arriba)
    import os, platform
    return {
        "ok": True,
        "component": "ops",
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "configuration": os.getenv("K_CONFIGURATION"),
        "project": os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT"),
        "base_url": os.getenv("NATACHA_BASE_URL"),
        "now_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
    }
