# routes/system_decisions.py
from fastapi import APIRouter
from ops.cognitive.decisions.model import CognitiveDecision
from ops.cognitive.decisions.writer import write_decision
from ops.cognitive.decisions.reader import list_decisions

router = APIRouter(prefix="/ops/cognitive", tags=["cognitive"])


@router.post("/decide")
def decide(payload: dict):
    decision = CognitiveDecision(**payload)
    return write_decision(decision)


@router.get("/decisions")
def get_decisions(limit: int = 20):
    return {
        "status": "ok",
        "decisions": list_decisions(limit),
    }
