# ops/system/checkpoint_writer.py
from datetime import datetime
from ops.timeline.writer import write_event


def write_checkpoint(label: str):
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "checkpoint",
        "label": label,
        "confidence": "high",
    }

    write_event(event)
    return {
        "status": "ok",
        "checkpoint": label,
        "timestamp": event["timestamp"],
    }
