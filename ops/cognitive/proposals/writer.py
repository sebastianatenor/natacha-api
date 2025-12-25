# ops/cognitive/proposals/writer.py
import uuid
from typing import Dict, Any, List

from ops.timeline.writer import write_event
from .model import CognitiveProposal


def write_proposal(data: Dict[str, Any]) -> CognitiveProposal:
    """
    Canonical writer for cognitive proposals.
    Adds identity + timestamp and persists to timeline.
    """

    proposal = CognitiveProposal(
        id=str(uuid.uuid4()),
        timestamp=CognitiveProposal.now_iso(),
        **data,
    )

    write_event(
        kind="cognitive_proposal",  # timeline event type
        subsystem="proposal",
        state=proposal.status,
        revision=proposal.source_revision,
        confidence=str(proposal.confidence),
        details=proposal.dict(),
    )

    return proposal


def write_proposals_bulk(
    proposals_data: List[Dict[str, Any]],
) -> List[CognitiveProposal]:
    written: List[CognitiveProposal] = []

    for data in proposals_data:
        written.append(write_proposal(data))

    return written
