# routes/system_diagnose.py

from fastapi import APIRouter
from typing import Dict, Any

from routes.context_unified import unified_context
from ops.system_interpreter import interpret_system_state

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/diagnose")
def system_diagnose() -> Dict[str, Any]:
    """
    Diagnóstico del sistema.
    La memoria se evalúa SOLO desde context/unified.
    """

    # Estado crudo del sistema
    from routes.system_state import system_state
    raw_state = system_state()

    # Forzamos lectura de contexto (esto activa lazy memory si existe)
    context = unified_context(user_id="__system__", limit=5)

    memory_ok = context["memory"]["items_count"] > 0

    # Inyectamos verdad real
    raw_state["memory"]["store_loaded"] = memory_ok
    raw_state["memory"]["items_count"] = context["memory"]["items_count"]

    diagnosis = interpret_system_state(raw_state)

    return {
        "state": raw_state,
        "diagnosis": diagnosis,
    }
