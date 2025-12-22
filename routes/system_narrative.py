from fastapi import APIRouter

from ops.timeline.reader import read_events
from ops.symbolic.rules_v2 import evaluate_symbolic_health
from ops.symbolic.narrative import (
    derive_state_from_events,
    build_narrative,
)

router = APIRouter(prefix="/ops/system", tags=["system"])


@router.get("/narrative")
def system_narrative():
    events = read_events()

    derived_state = derive_state_from_events(events)
    rules = evaluate_symbolic_health(derived_state)

    narrative = build_narrative(
        derived_state=derived_state,
        rules=rules,
    )

    return {
        "status": "ok",
        "narrative": narrative,
        "derived_state": derived_state,
    }
