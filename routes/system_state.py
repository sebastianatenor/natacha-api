# routes/system_state.py
"""
/system/state
Estado del sistema VERIFICADO (AGENTE_VERAZ)

ÚNICO endpoint autorizado a exponer runtime real.
NO debe ser usado por /agent/interact.
"""

import os
import time
from fastapi import APIRouter

from ops.memory.canonical_state import memory_state
from ops.cognitive.state_registry import read_last_cognitive_state

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/state")
def system_state():
    now = time.time()

    runtime = {
        "verified": True,
        "cloud_run": os.getenv("K_SERVICE") is not None,
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "python": os.getenv("PYTHON_VERSION", "3.10.x"),
    }

    semantic_state = read_last_cognitive_state("semantic")

    semantic = {
        "verified": semantic_state is not None,
        "state": semantic_state["state"] if semantic_state else "unknown",
        "loaded": semantic_state is not None and semantic_state.get("state") == "loaded",
        "confidence": semantic_state.get("confidence") if semantic_state else "unknown",
        "last_update": semantic_state.get("timestamp") if semantic_state else None,
        "hf_token_present": bool(os.getenv("HF_TOKEN")),
    }

    return {
        "status": "ok",
        "verified": True,
        "timestamp": now,
        "runtime": runtime,
        "semantic": semantic,
        "memory": memory_state(),
    }
