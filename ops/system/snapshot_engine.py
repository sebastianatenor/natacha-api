from datetime import datetime
from ops.timeline.writer import write_event

def create_snapshot(reason: str = "auto"):
    write_event(
        kind="snapshot",
        subsystem="system",
        state="captured",
        revision="v17",
        confidence=0.8,
        details={
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
        }
    )
