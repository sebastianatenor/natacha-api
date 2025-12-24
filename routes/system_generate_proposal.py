from fastapi import APIRouter

from ops.cognitive.proposals.generator import generate_proposal_if_needed

router = APIRouter(tags=["cognitive"])


@router.post("/ops/cognitive/proposals/generate")
def generate_proposal():
    proposal = generate_proposal_if_needed()

    if not proposal:
        return {
            "status": "noop",
            "detail": "No proposal generated",
        }

    return {
        "status": "ok",
        "proposal": proposal,
    }
