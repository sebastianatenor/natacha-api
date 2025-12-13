from fastapi import APIRouter
from typing import Dict, Any
import os

from routes.system_state import system_state
from ops.system_interpreter import interpret_system_state

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/diagnose")
def system_diagnose() -> Dict[str, Any]:
    """
    Diagnóstico interpretado del sistema.

    IMPORTANTE:
    - La memoria es LAZY.
    - 'store_loaded = false' NO es error si el archivo existe.
    - El diagnóstico se basa en disponibilidad real, no en carga en runtime.
    """

    raw_state = system_state()

    # ---------------------------------------
    # Corrección conceptual de memoria (LAZY)
    # ---------------------------------------
    memory_store_path = "/tmp/memory_store.jsonl"

    memory_available = os.path.exists(memory_store_path)

    # Inyectamos el concepto correcto antes de interpretar
    raw_state["memory"]["store_available"] = memory_available

    # Interpretación final
    diagnosis = interpret_system_state(raw_state)

    return {
        "state": raw_state,
        "diagnosis": diagnosis
    }
