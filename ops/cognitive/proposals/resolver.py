# ops/cognitive/proposals/resolver.py

from ops.timeline.reader import read_events


def find_proposal_by_fingerprint(fingerprint: str):
    """
    Devuelve la proposal existente para un fingerprint dado,
    o None si no existe.
    """
    events = read_events()

    for e in reversed(events):
        if e.get("kind") != "cognitive_proposal":
            continue

        details = e.get("details", {})
        if details.get("fingerprint") == fingerprint:
            return details

    return None
