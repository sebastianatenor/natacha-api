from fastapi import APIRouter, Query
from unified_core.memory_paths import get_canonical_memory_path
import json

router = APIRouter(tags=["ops-memory"])

@router.get("/ops/memory/recent")
def ops_memory_recent(limit: int = Query(20, ge=1, le=200)):
    path = get_canonical_memory_path()
    items = []

    if not path.exists():
        return {
            "status": "ok",
            "count": 0,
            "items": [],
            "source": str(path),
        }

    with path.open("r", encoding="utf-8") as f:
        for line in reversed(f.readlines()):
            if len(items) >= limit:
                break
            try:
                record = json.loads(line)
            except Exception:
                continue

            items.append(record)

    return {
        "status": "ok",
        "count": len(items),
        "items": items,
        "source": str(path),
    }
