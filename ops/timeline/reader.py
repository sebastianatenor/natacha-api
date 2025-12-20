import json
from unified_core.memory_paths import get_canonical_memory_path

def read_events():
    path = get_canonical_memory_path()
    events = []

    if not path.exists():
        return events

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("kind") in (
                    "self_checkpoint",
                    "daily_snapshot",
                    "cognitive_state"
                ):
                    events.append(obj)
            except Exception:
                continue

    events.sort(key=lambda x: x.get("timestamp", ""))
    return events
