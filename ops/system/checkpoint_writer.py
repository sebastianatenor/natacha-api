# ops/system/checkpoint_writer.py
from datetime import datetime
from ops.timeline.writer import write_event


def write_checkpoint(label: str):
    """
    B13-safe checkpoint.
    No depende de semantic, memory index ni cognitive state.
    Solo deja una marca canónica en el timeline.
    """

    event = write_event(
        kind="system_checkpoint",
        subsystem="system",
        state="stable",
        revision=label,
        confidence=1.0,
        details={
            "label": label,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "note": "B13 stable checkpoint (timeline-only)",
        },
    )

    return {
        "status": "ok",
        "checkpoint": label,
        "timestamp": event["timestamp"],
    }
