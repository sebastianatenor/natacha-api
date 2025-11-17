from fastapi import APIRouter, Body
import asyncio, traceback
from datetime import datetime, timezone
from routes.memory_routes import get_db as _get_db

router = APIRouter()

def _now_iso():
    return datetime.now(timezone.utc).isoformat()


@router.post("/tasks/add")
async def tasks_add(payload: dict = Body(...)):
    try:
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
        return {"status": "ok", "task_id": doc_ref.id}

    except Exception as e:
        print("[ERROR] tasks_add exception:", e)
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
