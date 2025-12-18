# ops/cognitive/state_registry.py
"""
Cognitive State Registry
-----------------------
Fuente de verdad persistente del estado cognitivo.
NO ejecuta lógica pesada.
NO instancia subsistemas.
"""

import json
from datetime import datetime
from typing import Optional, Dict

from unified_core.memory_paths import get_canonical_memory_path

MEMORY_PATH = get_canonical_memory_path()

def write_cognitive_state(
    subsystem: str,
    state: str,
    revision: str,
    confidence: str = "medium",
    details: Optional[Dict] = None
):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "cognitive_state",
        "subsystem": subsystem,
        "state": state,
        "revision": revision,
        "confidence": confidence,
        "details": details or {}
    }

    with MEMORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return record


def read_last_cognitive_state(subsystem: str) -> Optional[Dict]:
    if not MEMORY_PATH.exists():
        return None

    last = None
    with MEMORY_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                obj = json.loads(line)
            except Exception:
                continue

            if obj.get("kind") == "cognitive_state" and obj.get("subsystem") == subsystem:
                last = obj

    return last
