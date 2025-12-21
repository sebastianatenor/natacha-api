from fastapi import APIRouter

from ops.timeline.reader import read_events
from ops.symbolic.rules_v2 import evaluate_symbolic_health
from ops.symbolic.narrative import (
    derive_state_from_events,
    build_narrative,
)

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/diagnose")
def system_diagnose():
    # 1. Leer eventos cognitivos
    events = read_events()

    # 2. Derivar estado
    derived_state = derive_state_from_events(events)

    # 3. Evaluar reglas simbólicas
    rules = evaluate_symbolic_health(derived_state)

    # 4. Construir narrativa (🔥 FIRMA CORRECTA 🔥)
    narrative = build_narrative(
        derived_state=derived_state,
        rules=rules,
    )

    return {
        "status": "ok",
        "diagnosis": narrative,
        "derived_state": derived_state,
    }
