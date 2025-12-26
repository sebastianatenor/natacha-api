# ops/cognitive/decisions/reader.py
from ops.timeline.reader import read_events


def list_decisions(limit: int = 20):
    events = read_events()

    decisions = [
        e for e in events
        if e.get("kind") == "cognitive_decision"
    ]

    return decisions[-limit:]
