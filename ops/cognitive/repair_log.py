# ops/cognitive/repair_log.py
from datetime import datetime, timezone
from typing import Dict, Any

from ops.timeline.writer import write_event


def log_repair_proposal(drift: Dict[str, Any], baseline: Dict[str, Any]):
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": "self_repair_proposal",
        "drift": drift,
        "baseline_revision": baseline.get("revision"),
        "confidence": "high",
    }

    write_event(event)
