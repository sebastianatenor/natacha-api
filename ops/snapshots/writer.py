from datetime import datetime
from ops.system.state_aggregator import compute_system_state
from ops.timeline.writer import write_event


def write_snapshot(label: str = "auto"):
    state = compute_system_state()

    event = {
        "label": label,
        "state": state,
    }

    write_event(
        kind="snapshot",
        subsystem="system",
        state="captured",
        revision="v17",
        confidence=1.0,
        details=event,
    )

    return {
        "status": "ok",
        "label": label,
        "timestamp": datetime.utcnow().isoformat(),
    }
