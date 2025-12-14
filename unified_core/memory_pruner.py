import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

from unified_core.memory_lazy import (
    is_memory_available,
    get_memory_path,
)

CRITICAL_TAGS = {
    "project",
    "client",
    "contract",
    "decision",
    "LLVC",
}

DEFAULT_MAX_DAYS = 45


def _is_critical(item: Dict[str, Any]) -> bool:
    tags = set(item.get("tags", []))
    return len(tags & CRITICAL_TAGS) > 0


def _is_older_than(item: Dict[str, Any], days: int) -> bool:
    ts = (
        item.get("meta", {}).get("timestamp")
        or item.get("timestamp")
    )
    if not ts:
        return False

    try:
        dt = datetime.fromisoformat(ts.replace("Z", ""))
    except Exception:
        return False

    return dt < datetime.utcnow() - timedelta(days=days)


def prune_memory(
    max_days: int = DEFAULT_MAX_DAYS,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """
    Prune seguro de memoria NDJSON.
    - Respeta items críticos
    - Cloud Run safe
    """
    if not is_memory_available():
        return {
            "status": "skipped",
            "reason": "memory_not_available",
        }

    path = get_memory_path()
    if not path or not os.path.exists(path):
        return {
            "status": "skipped",
            "reason": "memory_file_missing",
        }

    kept: List[Dict[str, Any]] = []
    removed: List[Dict[str, Any]] = []

    with open(path, "r") as f:
        for line in f:
            try:
                item = json.loads(line)
            except Exception:
                continue

            if _is_critical(item):
                kept.append(item)
            elif _is_older_than(item, max_days):
                removed.append(item)
            else:
                kept.append(item)

    if not dry_run:
        with open(path, "w") as f:
            for item in kept:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    return {
        "status": "ok",
        "dry_run": dry_run,
        "max_days": max_days,
        "kept_items": len(kept),
        "removed_items": len(removed),
        "total_before": len(kept) + len(removed),
    }
