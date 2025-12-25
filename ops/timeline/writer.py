# ops/timeline/writer.py
import json
from datetime import datetime
from typing import Dict, Any

from ops.timeline.utils import get_timeline_path


def write_event(
    *,
    kind: str,
    subsystem: str,
    state: str,
    revision: str,
    confidence: float,
    details: Dict[str, Any],
):
    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "kind": kind,
        "subsystem": subsystem,
        "state": state,
        "revision": revision,
        "confidence": confidence,
        "details": details,
    }

    path = get_timeline_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

    return event
