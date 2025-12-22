from datetime import datetime, timezone
import json
from unified_core.memory_paths import get_canonical_memory_path


def write_memory_note(content: str, tags: list[str] | None = None):
    path = get_canonical_memory_path()

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": "memory_note",
        "content": content,
        "tags": tags or [],
        "confidence": "high",
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event
