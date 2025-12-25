# ops/timeline/reader.py
import json
from typing import List, Dict, Any

from ops.timeline.utils import get_timeline_path


def read_events() -> List[Dict[str, Any]]:
    path = get_timeline_path()

    if not path.exists():
        return []

    events = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue

    return events
