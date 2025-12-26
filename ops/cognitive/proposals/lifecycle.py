# ops/cognitive/proposals/lifecycle.py
from typing import Dict, Any
from ops.timeline.reader import read_events
from ops.timeline.writer import write_event


VALID_TRANSITIONS = {
    "proposed": {"accepted", "rejected"},
    "accepted": set(),
    "rejected": set(),
}


def _latest_state(proposal_id: str) -> str | None:
    events = read_events()
    for e in reversed(events):
        if e.get("kind") == "cognitive_proposal_lifecycle":
            d = e.get("details", {})
            if d.get("proposal_id") == proposal_id:
                return d.get("new_state")
    return None


def transition_proposal(
    proposal_id: str,
    new_state: str,
    actor: str,
    rationale: str,
    revision: str,
) -> Dict[str, Any]:
    """
    Append-only lifecycle transition.
    """
    current = _latest_state(proposal_id) or "proposed"

    if new_state not in VALID_TRANSITIONS.get(current, set()):
        return {
            "status": "error",
            "error": "invalid_transition",
            "current": current,
            "requested": new_state,
        }

    write_event(
        kind="cognitive_proposal_lifecycle",
        subsystem="proposal",
        state=new_state,
        revision=revision,
        confidence=1.0,
        details={
            "proposal_id": proposal_id,
            "previous_state": current,
            "new_state": new_state,
            "actor": actor,
            "rationale": rationale,
        },
    )

    return {
        "status": "ok",
        "proposal_id": proposal_id,
        "from": current,
        "to": new_state,
    }
