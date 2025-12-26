# ops/cognitive/proposals/writer.py

from typing import Dict, Any, List, Optional
from ops.timeline.writer import write_event
from ops.timeline.reader import read_events
from .model import CognitiveProposal


def _find_existing_proposal_by_fingerprint(
    fingerprint: str,
) -> Optional[CognitiveProposal]:
    events = read_events()

    for e in events:
        if e.get("kind") != "cognitive_proposal":
            continue

        details = e.get("details", {})
        if details.get("fingerprint") == fingerprint:
            return CognitiveProposal(**details)

    return None


def write_proposal(data: Dict[str, Any]) -> CognitiveProposal:
    """
    B16 — Idempotent proposal writer (fingerprint-based)
    """

    fingerprint = data.get("fingerprint")

    if fingerprint:
        existing = _find_existing_proposal_by_fingerprint(fingerprint)
        if existing:
            return existing

    proposal = CognitiveProposal(
        id=CognitiveProposal.new_id(),
        timestamp=CognitiveProposal.now_iso(),
        **data,
    )

    write_event(
        kind="cognitive_proposal",
        subsystem="proposal",
        state=proposal.status,
        revision=proposal.source_revision,
        confidence=str(proposal.confidence),
        details=proposal.dict(),
    )

    return proposal
