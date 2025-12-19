# routes/system_last_checkpoint.py
from fastapi import APIRouter
import json
from unified_core.memory_paths import get_canonical_memory_path

router = APIRouter(prefix="/ops/system", tags=["System"])

MEMORY_PATH = get_canonical_memory_path()

@router.get("/last_checkpoint")
def last_checkpoint():
    """
    Devuelve el último self_checkpoint registrado.
    Read-only. Observacional. Cloud Run safe.
    """

    if not MEMORY_PATH.exists():
        return {
            "status": "error",
            "detail": "memory_store.jsonl not found"
        }

    last = None

    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") == "self_checkpoint":
                    last = obj
            except Exception:
                continue

    if not last:
        return {
            "status": "empty",
            "detail": "No self_checkpoint found"
        }

    return {
        "status": "ok",
        "checkpoint": last
    }
