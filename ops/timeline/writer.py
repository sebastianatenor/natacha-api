import uuid
from datetime import datetime
from ops.timeline.utils import get_timeline_path
import json

def write_event(
    kind: str,
    subsystem: str,
    state: str,
    revision: str,
    confidence,
    details: dict,
):
    event = {
        "event_id": str(uuid.uuid4()),  # ✅ CLAVE
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "kind": kind,
        "subsystem": subsystem,
        "state": state,
        "revision": revision,
        "confidence": confidence,
        "details": details,
    }

    path = get_timeline_path()
    with open(path, "a") as f:
        f.write(json.dumps(event) + "\n")

    return event
