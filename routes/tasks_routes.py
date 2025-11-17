from fastapi import APIRouter, Body
import asyncio, traceback
from datetime import datetime, timezone
from routes.memory_routes import get_db as _get_db

router = APIRouter()

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

# -------------------------
# Core logic (no endpoint)
# -------------------------
async def _create_task(payload: dict):
    db = _get_db()
    col = db.collection("tasks")
    doc_ref = col.document()
    doc = {
        "title": payload.get("title", "Untitled task"),
        "created_at": _now_iso(),
    }

    result = doc_ref.set(doc)
    if asyncio.iscoroutine(result):
        print("[DEBUG] Awaiting coroutine from Firestore set()")
        await result

    print("[OK] Task created:", doc_ref.id)
    return {"task_id": doc_ref.id, "created_at": doc["created_at"]}

# -------------------------
# Public routes
# -------------------------
@router.post("/tasks/add")
async def tasks_add(payload: dict = Body(...)):
    try:
        result = await _create_task(payload)
        return {"status": "ok", **result}
    except Exception as e:
        print("[ERROR] tasks_add exception:", e)
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}

@router.get("/tasks/list")
async def tasks_list():
    db = _get_db()
    tasks = [d.to_dict() for d in db.collection("tasks").stream()]
    return {"status": "ok", "tasks": tasks}
