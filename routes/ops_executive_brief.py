from fastapi import APIRouter
from unified_core.memory_paths import get_canonical_memory_path
import json

router = APIRouter(tags=["executive"])

@router.get("/ops/executive/brief")
def executive_brief():
    path = get_canonical_memory_path()
    decisions = []

    if not path.exists():
        return {"status": "ok", "count": 0, "decisions": []}

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in reversed(lines):
        try:
            rec = json.loads(line)
        except Exception:
            continue

        meta = rec.get("meta") or {}
        if meta.get("kind") == "executive_decision" and meta.get("canonical") is True:
            decisions.append({
                "title": meta.get("title"),
                "decision": meta.get("decision"),
                "scope": meta.get("scope"),
                "rationale": meta.get("rationale"),
                "effects": meta.get("effects"),
                "timestamp": rec.get("timestamp"),
                "id": rec.get("id"),
            })

        if len(decisions) >= 20:
            break

    return {
        "status": "ok",
        "count": len(decisions),
        "decisions": decisions,
        "source": str(path),
    }
