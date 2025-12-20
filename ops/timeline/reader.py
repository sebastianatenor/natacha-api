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
                    "cognitive_state",
                ):
                    events.append(obj)
            except Exception:
                continue

    events.sort(key=lambda x: x.get("timestamp", ""))
    return events


def get_derived_state():
    events = read_events()

    snapshot_count = sum(1 for e in events if e.get("kind") == "daily_snapshot")
    checkpoint_count = sum(1 for e in events if e.get("kind") == "self_checkpoint")

    semantic_loaded = any(
        e.get("kind") == "cognitive_state"
        and e.get("subsystem") == "semantic"
        and e.get("state") == "loaded"
        for e in events
    )

    if semantic_loaded and snapshot_count > 0:
        maturity = "high"
    elif snapshot_count > 0:
        maturity = "developing"
    else:
        maturity = "early"

    return {
        "semantic_loaded": semantic_loaded,
        "snapshot_count": snapshot_count,
        "checkpoint_count": checkpoint_count,
        "maturity": maturity,
    }
