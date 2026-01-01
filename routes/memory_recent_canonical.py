from fastapi import APIRouter
from unified_core.memory_paths import get_canonical_memory_path
import json

router = APIRouter(prefix="/memory", tags=["memory"])

@router.get("/recent")
def memory_recent(limit: int = 20):
    path = get_canonical_memory_path()

    if not path.exists():
        return {
            "status": "ok",
            "count": 0,
            "items": [],
            "source": str(path),
        }

    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except Exception:
                continue

    items = items[-limit:]

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
        "source": str(path),
    }
