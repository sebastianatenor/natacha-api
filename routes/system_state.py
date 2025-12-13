import os
import time
from fastapi import APIRouter
from unified_core.memory_lazy import get_memory_index

router = APIRouter(tags=["system"])

@router.get("/ops/system/state")
def system_state():
    """
    Estado real del sistema (Cloud Run safe).
    SOLO observabilidad. No ejecuta lógica pesada.
    """

    now = time.time()

    # =========================
    # Runtime
    # =========================
    in_cloud_run = os.getenv("K_SERVICE") is not None

    runtime = {
        "cloud_run": in_cloud_run,
        "service": os.getenv("K_SERVICE"),
        "revision": os.getenv("K_REVISION"),
        "python": os.getenv("PYTHON_VERSION", "3.10.x"),
    }

    # =========================
    # Semantic Core
    # =========================
    semantic_loaded = False
    try:
        from unified_core.semantic_core import get_semantic_core
        core = get_semantic_core()
        semantic_loaded = core.is_loaded()
    except Exception:
        semantic_loaded = False

    semantic = {
        "loaded": semantic_loaded,
        "hf_token_present": bool(os.getenv("HF_TOKEN")),
    }


    # =========================
    # Memory (source of truth)
    # =========================
    memory_index = get_memory_index()
    memory = memory_index.status()

    # =========================
    # Context / Introspection
    # =========================
    context = {
        "unified": "loaded"
    }

    introspection = {
        "history": "loaded",
        "meta": "loaded",
    }

    # =========================
    # Infra
    # =========================
    infra = {
        "health_routes": "loaded"
    }

    return {
        "timestamp": now,
        "runtime": runtime,
        "infra": infra,
        "semantic": semantic,
        "memory": memory,
        "context": context,
        "introspection": introspection,
    }
