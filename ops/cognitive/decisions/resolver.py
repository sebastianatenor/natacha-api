# ops/cognitive/decisions/resolver.py

import os
from typing import Optional
from ops.timeline.reader import read_events


def is_fingerprint_accepted(fingerprint: str) -> bool:
    """
    B16 resolver — timeline scoped

    - Respeta NATACHA_TIMELINE_PATH si existe
    - NO lee decisiones globales durante tests
    """

    events = read_events()

    for e in reversed(events):
        if e.get("kind") != "cognitive_decision":
            continue

        details = e.get("details", {})
        if details.get("fingerprint") != fingerprint:
            continue

        return details.get("decision") == "accepted"

    return False
