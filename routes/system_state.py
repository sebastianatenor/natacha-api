import os
import time
from fastapi import APIRouter

from ops.memory.canonical_state import memory_state
from ops.cognitive.state_registry import read_last_cognitive_state

router = APIRouter(prefix="/ops/system", tags=["System"])

@router.get("/state")
def system_state():
    now = time.time()

    runtime = {
        "cloud_run": os.getenv("K_SERVICE") is not None,
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "python": os.getenv("PYTHON_VERSION", "3.10.x"),
    }

    semantic_state = read_last_cognitive_state("semantic")

    semantic = {
        "state": semantic_state["state"] if semantic_state else "not_attempted",
        "loaded": semantic_state is not None and semantic_state["state"] == "loaded",
        "confidence": semantic_state["confidence"] if semantic_state else "unknown",
        "last_update": semantic_state["timestamp"] if semantic_state else None,
        "hf_token_present": bool(os.getenv("HF_TOKEN")),
    }

    return {
        "timestamp": now,
        "runtime": runtime,
        "semantic": semantic,
        "memory": memory_state(),
        "context": {"unified": "loaded"},
        "introspection": {"history": "loaded", "meta": "loaded"},
        "infra": {"health_routes": "loaded"},
    }
