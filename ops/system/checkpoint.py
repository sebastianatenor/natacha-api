from datetime import datetime
from ops.timeline.writer import write_event

def create_checkpoint(label: str):
    write_event(
        kind="checkpoint",
        subsystem="cognitive",
        state="saved",
        revision="v17",
        confidence=0.9,
        details={
            "label": label,
            "timestamp": datetime.utcnow().isoformat()
        }
    )
