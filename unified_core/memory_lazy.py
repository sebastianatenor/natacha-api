"""
memory_lazy.py — Unified Memory Loader (Cloud Run safe)

- Lazy initialization
- No import-time side effects
- Uses NDJSON store in /tmp
"""

from typing import Optional
from pathlib import Path


_MEMORY_INDEX = None


def get_memory_index():
    global _MEMORY_INDEX

    if _MEMORY_INDEX is not None:
        return _MEMORY_INDEX

    # Lazy import (CRÍTICO)
    from unified_core.memory_unified_index import UnifiedMemoryIndex

    store_path = Path("/tmp/memory_store.jsonl")

    memory = UnifiedMemoryIndex(
        store_path=store_path,
        auto_load=True,   # carga el NDJSON al primer uso
    )

    _MEMORY_INDEX = memory
    return memory
