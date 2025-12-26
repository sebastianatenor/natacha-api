# ops/cognitive/decisions/resolver.py

from ops.timeline.reader import read_events


def is_proposal_accepted(proposal_id: str) -> bool:
    """
    Returns True if the proposal has an ACCEPTED decision.
    Timeline is the source of truth.
    """

    events = read_events()

    for e in reversed(events):
        if e.get("kind") != "cognitive_decision":
            continue

        d = e.get("details", {})
        if (
            d.get("proposal_id") == proposal_id
            and d.get("decision") == "accepted"
        ):
            return True

    return False
