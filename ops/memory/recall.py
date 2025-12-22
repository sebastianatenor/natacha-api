"""
Semantic + Timeline Memory Recall
"""

from ops.timeline.reader import read_events


def recall_recent(limit: int = 20):
    events = read_events()
    return events[-limit:]


def recall_by_subsystem(subsystem: str, limit: int = 10):
    events = [
        e for e in read_events()
        if e.get("subsystem") == subsystem
    ]
    return events[-limit:]


def recall_decisions(limit: int = 10):
    events = [
        e for e in read_events()
        if e.get("kind") == "decision"
    ]
    return events[-limit:]
