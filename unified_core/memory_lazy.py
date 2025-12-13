"""
memory_lazy.py — Unified Memory Loader (Cloud Run safe)

- Lazy initialization
- No import-time side effects
- Uses NDJSON store in /tmp
"""

from pathlib import Path

_MEMORY_INDEX = None


def get_memory_index():
    global _MEMORY_INDEX

    if _MEMORY_INDEX is not None:
        return _MEMORY_INDEX

    # 🔴 IMPORT CORRECTO (engine real)
    from unified_core.memory_unified import MemoryUnified

    store_path = Path("/tmp/memory_store.jsonl")

    memory = MemoryUnified(
        store_path=str(store_path),
        lazy=True,
    )

    _MEMORY_INDEX = memory
    return memory
