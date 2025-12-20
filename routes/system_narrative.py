from fastapi import APIRouter
from ops.timeline.reader import read_events
from ops.symbolic.rules_v2 import evaluate_symbolic_health
from ops.symbolic.narrative import build_cognitive_narrative

router = APIRouter(prefix="/ops/system", tags=["system"])

@router.get("/narrative")
def get_cognitive_narrative():
    events = read_events()
    derived_state = build_cognitive_narrative(events)
    rules = evaluate_symbolic_health(derived_state)

    narrative = build_cognitive_narrative(
        events=events,
        derived_state=derived_state,
        rules=rules,
    )

    return {
        "status": "ok",
        "narrative": narrative,
        "derived_state": derived_state,
    }
