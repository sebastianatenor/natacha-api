from fastapi import APIRouter
import os
from datetime import datetime, timezone

router = APIRouter(
    prefix="/ops/system",
    tags=["system"],
)

@router.get("/state")
def system_state():
    """
    Estado REAL del sistema.
    No infiere, no razona, no evalúa.
    Lee únicamente runtime y memoria efectiva.
    """

    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "project": os.getenv("GOOGLE_CLOUD_PROJECT"),
        "environment": "cloud_run" if os.getenv("K_SERVICE") else "local",
        "flags": {
            "COGNITIVE_FREEZE": os.getenv("COGNITIVE_FREEZE"),
            "NATACHA_FAST_BOOT": os.getenv("NATACHA_FAST_BOOT"),
        },
        "memory": {},
        "semantic": {},
        "timeline": {},
    }

    # -----------------------------
    # MEMORY (canónica)
    # -----------------------------
    try:
        from unified_core.memory_paths import get_canonical_memory_path
        path = get_canonical_memory_path()
        state["memory"] = {
            "canonical_path": str(path),
            "exists": path.exists(),
            "size_bytes": path.stat().st_size if path.exists() else 0,
        }
    except Exception as e:
        state["memory"] = {
            "error": str(e)
        }

    # -----------------------------
    # SEMANTIC ENGINE
    # -----------------------------
    try:
        from unified_core.semantic_runtime import semantic_is_loaded
        state["semantic"] = {
            "loaded": bool(semantic_is_loaded())
        }
    except Exception:
        state["semantic"] = {
            "loaded": False
        }

    # -----------------------------
    # TIMELINE / EVENTS
    # -----------------------------
    try:
        from ops.timeline.reader import read_events
        events = read_events()
        state["timeline"] = {
            "events_total": len(events),
            "last_event": events[-1] if events else None,
        }
    except Exception as e:
        state["timeline"] = {
            "error": str(e)
        }

    return {
        "status": "ok",
        "state": state
    }
