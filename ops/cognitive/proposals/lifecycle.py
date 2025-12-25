# ops/cognitive/proposals/lifecycle.py
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ops.timeline.reader import read_events
from .utils import compute_proposal_hash


def enrich_with_lifecycle(
    proposals: List[Dict[str, Any]],
    ttl_days: int = 7,
) -> List[Dict[str, Any]]:
    """
    Adds lifecycle metadata:
    - dedupe
    - first_seen / last_seen
    - occurrences
    - expired
    """

    now = datetime.utcnow()
    timeline = read_events()

    existing = {
        e["details"].get("proposal_hash"): e
        for e in timeline
        if e.get("kind") == "cognitive_proposal"
    }

    enriched: List[Dict[str, Any]] = []

    for p in proposals:
        h = compute_proposal_hash(p)
        ts = now.isoformat() + "Z"

        if h in existing:
            prev = existing[h]["details"]
            first_seen = prev.get("first_seen", prev.get("timestamp"))
            occurrences = prev.get("occurrences", 1) + 1
        else:
            first_seen = ts
            occurrences = 1

        expired = False
        if first_seen:
            age = now - datetime.fromisoformat(first_seen.replace("Z", ""))
            expired = age > timedelta(days=ttl_days)

        p.update({
            "proposal_hash": h,
            "first_seen": first_seen,
            "last_seen": ts,
            "occurrences": occurrences,
            "expired": expired,
        })

        enriched.append(p)

    return enriched
