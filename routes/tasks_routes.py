from fastapi import APIRouter, Body
import asyncio, traceback, inspect
from datetime import datetime, timezone
from routes.memory_routes import get_db as _get_db

router = APIRouter()

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

# -------------------------
# Core logic (safe)
# -------------------------
async def _create_task(payload: dict):
    try:
        db = _get_db()
        if inspect.iscoroutine(db):
            print("[DEBUG] Awaiting coroutine from get_db()")
            db = await db

        col = db.collection("tasks")
        if inspect.iscoroutine(col):
            print("[DEBUG] Awaiting coroutine from db.collection()")
            col = await col

        doc_ref = col.document()
        if inspect.iscoroutine(doc_ref):
            print("[DEBUG] Awaiting coroutine from col.document()")
            doc_ref = await doc_ref

        doc = {
            "title": payload.get("title", "Untitled task"),
            "created_at": _now_iso(),
        }

        result = doc_ref.set(doc)
        if inspect.iscoroutine(result):
            print("[DEBUG] Awaiting coroutine from Firestore set()")
            await result

        print("[OK] Task created:", getattr(doc_ref, "id", "<no-id>"))
        return {"task_id": getattr(doc_ref, "id", "unknown"), "created_at": doc["created_at"]}

    except Exception as e:
        print("[ERROR] _create_task exception:", e)
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}

# -------------------------
# Public routes
# -------------------------
@router.post("/tasks/add")
async def tasks_add(payload: dict = Body(...)):
    result = await _create_task(payload)
    return result
