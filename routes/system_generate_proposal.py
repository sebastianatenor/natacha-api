# routes/system_generate_proposal.py
from fastapi import APIRouter
from ops.system.perception_provider import read_system_perception
from ops.timeline.reader import read_events
from ops.cognitive.signals.engine import collect_signals
from ops.cognitive.proposals.mapper import proposals_from_signals
from ops.cognitive.proposals.intelligence import enrich_and_dedup
from ops.cognitive.proposals.persist import persist_proposals

router = APIRouter(prefix="/ops/cognitive", tags=["cognitive"])


@router.post("/proposals/generate")
def generate_and_persist_proposals():
    perception = read_system_perception()
    events = read_events()

    signals = collect_signals(
        perception,
        {"timeline_events": len(events)}
    )

    raw = proposals_from_signals(
        signals,
        source_revision="B14.4"
    )

    final = enrich_and_dedup(raw)

    result = persist_proposals(final, revision="B14.4")

    return {
        "status": "ok",
        "signals": len(signals),
        "proposals": len(final),
        "persist": result,
    }
