# routes/system_guardrail.py

from fastapi import APIRouter, Query
from ops.cognitive.guardrail import evaluate_guardrail
from routes.system_executive_state import get_executive_state

router = APIRouter(prefix="/system/guardrail", tags=["system"])

@router.get("/check")
def check_action(action: str = Query(...)):
    """
    Evalúa si una acción está permitida por el estado ejecutivo actual.
    """

    executive = get_executive_state()

    if not executive.get("locked"):
        return {
            "allowed": True,
            "reason": "system_unlocked",
            "action": action
        }

    decision = evaluate_guardrail(
        executive_state=executive,
        action=action
    )

    return decision
