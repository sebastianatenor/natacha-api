from fastapi import APIRouter
from typing import Dict, Any
import time

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/state")
def system_state() -> Dict[str, Any]:
    """
    Vista unificada del estado del sistema.
    NO ejecuta lógica nueva.
    SOLO agrega información existente.
    """

    state: Dict[str, Any] = {
        "timestamp": time.time(),
        "infra": {},
        "diagnostics": {},
        "introspection": {},
        "context": {}
    }

    # --------------------------------------------------
    # Infra (health / deps / source)
    # --------------------------------------------------
    try:
        from routes.health_route import health
        state["infra"]["health"] = "ok"
    except Exception as e:
        state["infra"]["health"] = f"error: {e}"

    try:
        from routes.health_route import deps
        state["infra"]["deps"] = "ok"
    except Exception as e:
        state["infra"]["deps"] = f"error: {e}"

    try:
        from routes.health_route import debug_source
        state["infra"]["debug_source"] = "ok"
    except Exception as e:
        state["infra"]["debug_source"] = f"error: {e}"

    # --------------------------------------------------
    # Diagnostics
    # --------------------------------------------------
    try:
        from ops.self_diagnostics import run_diagnostics
        state["diagnostics"]["self"] = "available"
    except Exception as e:
        state["diagnostics"]["self"] = f"error: {e}"

    # --------------------------------------------------
    # Introspection
    # --------------------------------------------------
    try:
        from ops.introspection.history_reader import read_history
        state["introspection"]["history"] = "available"
    except Exception as e:
        state["introspection"]["history"] = f"error: {e}"

    try:
        from ops.introspection.meta_reflect import meta_reflect
        state["introspection"]["meta"] = "available"
    except Exception as e:
        state["introspection"]["meta"] = f"error: {e}"

    # --------------------------------------------------
    # Context
    # --------------------------------------------------
    try:
        from routes.context_unified import router as context_router
        state["context"]["unified"] = "available"
    except Exception as e:
        state["context"]["unified"] = f"error: {e}"

    return state
