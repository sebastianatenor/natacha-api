from fastapi import APIRouter
from typing import Dict, Any

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
    """
    raw_state = system_state()
    diagnosis = interpret_system_state(raw_state)

    return {
        "state": raw_state,
        "diagnosis": diagnosis
    }
