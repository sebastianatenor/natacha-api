# routes/system_executive_state.py

import json
from fastapi import APIRouter
from unified_core.memory_paths import get_canonical_memory_path

router = APIRouter(prefix="/system/executive", tags=["system"])

@router.get("/state")
def get_executive_state():
    """
    Fuente de verdad ejecutiva del sistema.
    PRE-ML SAFE: solo lectura desde memoria canónica.
    """

    path = get_canonical_memory_path()

    if not path.exists():
        return {
            "status": "error",
            "reason": "canonical_memory_not_found",
            "locked": False
        }

    last_decision = None

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except Exception:
                continue

            meta = rec.get("meta") or {}
            if (
                meta.get("kind") == "executive_decision"
                and meta.get("canonical") is True
            ):
                last_decision = {
                    "id": rec.get("id"),
                    "timestamp": rec.get("timestamp"),
                    "label": meta.get("label"),
                    "scope": meta.get("scope"),
                }

    if not last_decision:
        return {
            "status": "ok",
            "locked": False,
            "mode": "pre-ml-unlocked",
            "source": "canonical_memory",
            "decision": None
        }

    return {
        "status": "ok",
        "locked": True,
        "mode": "pre-ml-unified",
        "source": "canonical_memory",
        "decision": last_decision
    }
