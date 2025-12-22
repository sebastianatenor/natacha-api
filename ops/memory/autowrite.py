"""
Autonomous Memory Writer
"""

import json
from unified_core.memory_paths import get_canonical_memory_path
from ops.memory.policy import should_write_memory, enrich_event


def maybe_write(event: dict) -> bool:
    """
    Escribe en memoria solo si la policy lo permite.
    """
    if not should_write_memory(event):
        return False

    event = enrich_event(event)
    path = get_canonical_memory_path()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return True
