from ops.system.state_aggregator import compute_system_state
from datetime import datetime

def write_snapshot():
    state = compute_system_state()
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "state": state,
    }

