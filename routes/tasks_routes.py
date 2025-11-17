from fastapi import APIRouter, Body, Query
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio, traceback

from routes.memory_routes import get_db as _get_db

router = APIRouter()

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.post("/tasks/add")
async def tasks_add(payload: dict = Body(...)) -> Dict[str, Any]:
    """
    Crea una tarea simple en Firestore, asegurando que cualquier operación async se espere correctamente.
    """
    try:
        db = _get_db()
        col = db.collection("tasks")
        now = _now_iso()
        doc_ref = col.document()
        task_id = doc_ref.id

        doc: Dict[str, Any] = {
            "user_id": payload.get("user_id"),
            "title": payload.get("title", "Untitled task"),
            "detail": payload.get("detail", ""),
            "project": payload.get("project", "default"),
            "channel": payload.get("channel", "default"),
            "due": payload.get("due") or "",
            "state": payload.get("state", "pending"),
            "evidence": payload.get("evidence") or [],
            "created_at": now,
            "updated_at": now,
            "source": "tasks_routes",
            "key": f"{payload.get('project','')}:{payload.get('title','')}:{task_id}",
        }

        # Ejecutar set() y esperar si es coroutine
        result = doc_ref.set(doc)
        if asyncio.iscoroutine(result):
            await result

        doc["id"] = task_id
        print(f"[OK] Task created: {task_id}")
        return doc

    except Exception as e:
        print("[ERROR] tasks_add exception ->", e)
        traceback.print_exc()
        return {"status": "error", "detail": str(e)}
