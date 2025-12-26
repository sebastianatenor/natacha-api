# ops/cognitive/proposals/persist.py
from typing import List, Dict, Any
from ops.timeline.reader import read_events
from ops.timeline.writer import write_event


def _existing_dedup_keys() -> set:
    events = read_events()
    keys = set()
    for e in events:
        if e.get("kind") == "cognitive_proposal":
            dk = e.get("details", {}).get("dedup_key")
            if dk:
                keys.add(dk)
    return keys


def persist_proposals(
    proposals: List[Dict[str, Any]],
    revision: str,
) -> Dict[str, Any]:
    """
    Persist proposals to timeline (idempotent by dedup_key).
    """
    existing = _existing_dedup_keys()
    written = 0
    skipped = 0

    for p in proposals:
        dk = p.get("dedup_key")
        if dk and dk in existing:
            skipped += 1
            continue

        write_event(
            kind="cognitive_proposal",
            subsystem="proposal",
            state="proposed",
            revision=revision,
            confidence=float(p.get("confidence", 0.5)),
            details=p,
        )
        written += 1

    return {
        "written": written,
        "skipped": skipped,
        "total": len(proposals),
    }
