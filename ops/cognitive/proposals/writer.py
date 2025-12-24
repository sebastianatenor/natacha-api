# ops/cognitive/proposals/writer.py
import uuid
from typing import Dict, Any

from ops.timeline.writer import write_event
from .model import CognitiveProposal


def write_proposal(data: Dict[str, Any]) -> CognitiveProposal:
    proposal = CognitiveProposal(
        id=str(uuid.uuid4()),
        timestamp=CognitiveProposal.now_iso(),
        **data
    )

    write_event(
        kind="cognitive_proposal",
        subsystem="proposal",
        state=proposal.status,
        revision=proposal.source_revision,
        confidence="medium",
        details=proposal.dict(),
    )

    return proposal
