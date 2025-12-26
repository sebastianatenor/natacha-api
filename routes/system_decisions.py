# routes/system_decisions.py
from fastapi import APIRouter
from ops.cognitive.decisions.model import CognitiveDecision
from ops.cognitive.decisions.writer import write_decision
from ops.cognitive.decisions.reader import list_decisions

router = APIRouter(prefix="/ops/cognitive", tags=["cognitive"])


@router.post("/decide")
def decide(payload: dict):
    """
    B16.5
    - Normaliza el payload
    - Asegura fingerprint si viene
    """

    decision_data = dict(payload)

    # 🔑 Si viene fingerprint, lo preservamos
    # (si no viene, queda None y no rompe nada)
    if "fingerprint" not in decision_data:
        decision_data["fingerprint"] = None

    xdecision = CognitiveDecision(**payload)
    return write_decision(decision)


@router.get("/decisions")
def get_decisions(limit: int = 20):
    return {
        "status": "ok",
        "decisions": list_decisions(limit),
    }
