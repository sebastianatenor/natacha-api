# ops/cognitive/auto_checkpoint.py
import os
import json
from datetime import datetime
from pathlib import Path

from ops.cognitive.state_registry import read_last_cognitive_state


def _get_memory_path() -> Path:
    """
    Devuelve el path canónico de memoria según el entorno.
    - Cloud Run: /tmp/memory_store.jsonl (o env override)
    - Local: memory_store.jsonl
    """
    if os.getenv("K_SERVICE"):
        return Path(os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl"))
    return Path("memory_store.jsonl")


def write_revision_checkpoint():
    revision = os.getenv("K_REVISION")
    if not revision:
        return

    memory_path = _get_memory_path()

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
            "notes": "Checkpoint automático por revisión."
        },
        "confidence": "high"
    }

    try:
        memory_path.parent.mkdir(parents=True, exist_ok=True)
        with memory_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(checkpoint, ensure_ascii=False) + "\n")

        print(f"[CHECKPOINT] Revision checkpoint written → {memory_path}")

    except Exception as e:
        print(f"[CHECKPOINT][ERROR] Could not write checkpoint: {e}")
