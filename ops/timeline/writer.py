import uuid
from datetime import datetime
from ops.timeline.utils import get_timeline_path
import json
import os

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

    # Sync a GCS solo en Cloud Run
    if os.getenv("K_SERVICE"):
        try:
            from ops.timeline.sync import sync_timeline_to_gcs
            sync_timeline_to_gcs()
        except Exception as e:
            print(f"[TIMELINE][WARN] sync skipped: {e}")

    return event
