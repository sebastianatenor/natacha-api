from fastapi import APIRouter

from ops.symbolic.rules_v2 import evaluate_symbolic_health
from ops.symbolic.narrative import build_narrative
from ops.timeline.reader import get_derived_state

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/diagnose")
def system_diagnose():
    """
    Diagnóstico cognitivo narrativo del sistema.
    Explica el estado actual y recomienda acciones.
    """

    derived_state = get_derived_state()
    rules = evaluate_symbolic_health(derived_state)
    narrative = build_narrative(derived_state, rules)

    return {
        "status": "ok",
        "diagnosis": narrative,
        "derived_state": derived_state,
    }
