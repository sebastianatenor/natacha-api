import os
from pathlib import Path


def get_canonical_memory_path() -> Path:
    """
    Canonical memory path.
    - Cloud Run  → /tmp/memory_store.jsonl
    - Local dev → ./memory_store.jsonl
    """
    if os.getenv("K_SERVICE"):
        return Path("/tmp/memory_store.jsonl")

    return Path("memory_store.jsonl")
