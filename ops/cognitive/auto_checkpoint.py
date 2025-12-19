from datetime import datetime
import json
import os

from unified_core.memory_paths import get_canonical_memory_path
from ops.cognitive.state_registry import read_last_cognitive_state


def write_revision_checkpoint():
    revision = os.getenv("K_REVISION")
    if not revision:
        return

    semantic = read_last_cognitive_state("semantic")

    checkpoint = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "self_checkpoint",
        "revision": revision,
        "observed_state": {
            "semantic": semantic
        },
        "self_reported_state": {
            "infra": "stable",
            "memory": "loaded",
            "context": "loaded",
            "semantic": semantic["state"] if semantic else "unknown",
            "notes": "Checkpoint automático por revisión (canonical)."
        },
        "confidence": "high"
    }

    path = get_canonical_memory_path()

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(checkpoint, ensure_ascii=False) + "\n")
