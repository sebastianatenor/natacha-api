# routes/system_proposal_lifecycle.py
from fastapi import APIRouter
from ops.cognitive.proposals.lifecycle import transition_proposal

router = APIRouter(prefix="/ops/cognitive/proposals", tags=["cognitive"])


@router.post("/{proposal_id}/accept")
def accept_proposal(
    proposal_id: str,
    payload: dict,
):
    return transition_proposal(
        proposal_id=proposal_id,
        new_state="accepted",
        actor=payload.get("actor", "human"),
        rationale=payload.get("rationale", ""),
        revision="B14.5",
    )


@router.post("/{proposal_id}/reject")
def reject_proposal(
    proposal_id: str,
    payload: dict,
):
    return transition_proposal(
        proposal_id=proposal_id,
        new_state="rejected",
        actor=payload.get("actor", "human"),
        rationale=payload.get("rationale", ""),
        revision="B14.5",
    )
