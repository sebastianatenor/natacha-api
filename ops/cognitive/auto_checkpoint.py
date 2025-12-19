from datetime import datetime
import json
import os
import time

from unified_core.memory_paths import get_canonical_memory_path
from ops.cognitive.state_registry import read_last_cognitive_state


def write_revision_checkpoint(retries: int = 5, wait: float = 1.0):
    revision = os.getenv("K_REVISION")
    if not revision:
        return

    path = get_canonical_memory_path()

    # Esperar a que la memoria exista (post GCS sync)
    for _ in range(retries):
        if path.exists() and path.stat().st_size > 0:
            break
        time.sleep(wait)
    else:
        print("[CHECKPOINT][WARN] canonical memory not ready")
        return

    semantic = read_last_cognitive_state("semantic")

    checkpoint = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "self_checkpoint",
        "revision": revision,
        "observed_state": {
            "semantic": semantic
        },
        "confidence": "high"
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(checkpoint, ensure_ascii=False) + "\n")

    print("[CHECKPOINT] self_checkpoint appended")
