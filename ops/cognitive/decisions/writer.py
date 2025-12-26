# ops/cognitive/decisions/writer.py
from ops.timeline.writer import write_event
from .model import CognitiveDecision


def write_decision(decision: CognitiveDecision):
    write_event(
        kind="cognitive_decision",
        subsystem="decision",
        state=decision.decision,
        revision="B15",
        confidence=decision.confidence,
        details=decision.dict(),
    )

    return {
        "status": "ok",
        "decision_id": decision.decision_id,
        "proposal_id": decision.proposal_id,
        "decision": decision.decision,
    }
