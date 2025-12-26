# ops/cognitive/decisions/resolver.py

from ops.timeline.reader import read_events


def is_fingerprint_accepted(fingerprint: str) -> bool:
    """
    B16 — Decision resolver (fingerprint-based)

    Una acción queda habilitada si existe una decisión ACCEPTED
    con el mismo fingerprint semántico.
    """

    if not fingerprint:
        return False

    events = read_events()

    for e in events:
        if e.get("kind") != "cognitive_decision":
            continue

        details = e.get("details", {})

        if details.get("decision") != "accepted":
            continue

        if details.get("fingerprint") == fingerprint:
            return True

    return False
