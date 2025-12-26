# ops/cognitive/approval_cache/cache.py

from datetime import datetime, timedelta
from ops.timeline.reader import read_events

WINDOW_HOURS = 24


def find_recent_decision(fingerprint: str):
    now = datetime.utcnow()
    events = read_events()

    for e in reversed(events):
        if e.get("kind") != "cognitive_decision":
            continue

        details = e.get("details", {})
        if details.get("fingerprint") != fingerprint:
            continue

        ts_raw = details.get("timestamp")
        if not ts_raw:
            continue

        ts = datetime.fromisoformat(ts_raw.replace("Z", ""))
        if now - ts <= timedelta(hours=WINDOW_HOURS):
            return details

    return None
