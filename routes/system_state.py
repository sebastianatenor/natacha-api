from fastapi import APIRouter
from typing import Dict, Any
import time
import os

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/state")
def system_state() -> Dict[str, Any]:
    """
    Vista unificada REAL del estado del sistema.
    SOLO LECTURA. CERO efectos colaterales.
    """

    state: Dict[str, Any] = {
        "timestamp": time.time(),
        "runtime": {},
        "infra": {},
        "semantic": {},
        "memory": {},
        "introspection": {},
        "context": {}
    }

    # --------------------------------------------------
    # Runtime / Entorno
    # --------------------------------------------------
    state["runtime"] = {
        "cloud_run": bool(os.getenv("K_SERVICE")),
        "revision": os.getenv("K_REVISION"),
        "service": os.getenv("K_SERVICE"),
        "python": os.getenv("PYTHON_VERSION"),
    }

    # --------------------------------------------------
    # Infra (health endpoints existen)
    # --------------------------------------------------
    try:
        import routes.health_route
        state["infra"]["health_routes"] = "loaded"
    except Exception as e:
        state["infra"]["health_routes"] = f"error: {e}"

    # --------------------------------------------------
    # Semantic Core (estado real)
    # --------------------------------------------------
    try:
        from unified_core.semantic_core import get_semantic_core
        core = get_semantic_core()
        state["semantic"] = {
            "loaded": core._model is not None,
            "hf_token_present": bool(os.getenv("HF_TOKEN")),
        }
    except Exception as e:
        state["semantic"] = {"error": str(e)}

    # --------------------------------------------------
    # Memory engine
    # --------------------------------------------------
    try:
        import routes.memory_unified
        state["memory"]["engine"] = "memory_unified"
    except Exception as e:
        state["memory"]["engine"] = f"error: {e}"

    try:
        path = "/app/memory_store.jsonl"
        state["memory"]["store_present"] = os.path.exists(path)
    except Exception as e:
        state["memory"]["store_present"] = f"error: {e}"

    # --------------------------------------------------
    # Introspection
    # --------------------------------------------------
    try:
        import ops.introspection.history_reader
        state["introspection"]["history"] = "loaded"
    except Exception as e:
        state["introspection"]["history"] = f"error: {e}"

    try:
        import ops.introspection.meta_reflect
        state["introspection"]["meta"] = "loaded"
    except Exception as e:
        state["introspection"]["meta"] = f"error: {e}"

    # --------------------------------------------------
    # Context
    # --------------------------------------------------
    try:
        import routes.context_unified
        state["context"]["unified"] = "loaded"
    except Exception as e:
        state["context"]["unified"] = f"error: {e}"

    return state
