# ops/cognitive/proposals/writer.py

import uuid
from typing import Dict, Any, List, Optional

from ops.timeline.writer import write_event
from ops.timeline.reader import read_events
from .model import CognitiveProposal


def _find_existing_proposal_by_fingerprint(fingerprint: str) -> Optional[CognitiveProposal]:
    """
    Busca en el timeline una proposal existente con el mismo fingerprint.
    """
    events = read_events()

    for e in reversed(events):  # más reciente primero
        if e.get("kind") != "cognitive_proposal":
            continue

        details = e.get("details", {})
        if details.get("fingerprint") == fingerprint:
            return CognitiveProposal(**details)

    return None


def write_proposal(data: Dict[str, Any]) -> CognitiveProposal:
    """
    Canonical, IDEMPOTENT writer for cognitive proposals (B16)

    - Reusa proposal si fingerprint ya existe
    - NO duplica timeline
    """

    fingerprint = data.get("fingerprint")
    if fingerprint:
        existing = _find_existing_proposal_by_fingerprint(fingerprint)
        if existing:
            return existing  # 🔁 IDÉNTICA proposal

    # ⬇️ crear nueva SOLO si no existe
    proposal = CognitiveProposal(
        id=str(uuid.uuid4()),
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


def write_proposals_bulk(
    proposals_data: List[Dict[str, Any]],
) -> List[CognitiveProposal]:
    return [write_proposal(data) for data in proposals_data]
