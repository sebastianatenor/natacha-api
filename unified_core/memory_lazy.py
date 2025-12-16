# unified_core/memory_lazy.py
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================
# MemoryIndex-like contract used by context_engine_v4
# - must provide: list_recent(limit=...)
# - should provide: store_loaded (bool)
# ============================================================


class NullMemoryIndex:
    """
    Safe fallback that never crashes.
    Provides the interface expected by context_engine_v4.
    """
    store_loaded: bool = False

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return []


class NDJSONMemoryIndex:
    """
    Minimal, Cloud Run safe index reading a local NDJSON file.
    Designed to keep fast-boot stable:
      - reads /tmp/memory_store.jsonl if present
      - returns recent entries (last N)
      - never raises to callers
    """

    def __init__(self, local_path: str):
        self.local_path = local_path
        self.store_loaded = False
        self._cache: List[Dict[str, Any]] = []

        self._load()

    def _load(self) -> None:
        try:
            p = Path(self.local_path)
            if not p.exists():
                self.store_loaded = False
                self._cache = []
                return

            items: List[Dict[str, Any]] = []
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        # Ensure dict
                        if isinstance(obj, dict):
                            items.append(obj)
                    except Exception:
                        # Ignore bad lines; never crash
                        continue

            self._cache = items
            self.store_loaded = True if items else True  # file present counts as loaded
        except Exception:
            self.store_loaded = False
            self._cache = []

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            if not self._cache:
                return []
            if limit <= 0:
                return []
            return self._cache[-limit:]
        except Exception:
            return []


# ============================================================
# Lazy singletons (safe for Cloud Run)
# ============================================================

_MEMORY_INDEX: Optional[Any] = None  # Any object with list_recent + store_loaded


def _build_index() -> Any:
    """
    Build a safe memory index.
    Priority:
      1) /tmp/memory_store.jsonl (Cloud Run sync target)
      2) fallback NullMemoryIndex
    """
    try:
        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        p = Path(local_path)
        if p.exists():
            return NDJSONMemoryIndex(local_path)
    except Exception:
        pass
    return NullMemoryIndex()


def get_memory_index() -> Any:
    """
    Main accessor used by unified_core.context_engine_v4.
    GUARANTEE: never returns dict; always returns MemoryIndex-like object.
    """
    global _MEMORY_INDEX
    if _MEMORY_INDEX is None:
        _MEMORY_INDEX = _build_index()
    # HARD GUARANTEE: avoid returning dict even if something poisoned the singleton
    if isinstance(_MEMORY_INDEX, dict):
        _MEMORY_INDEX = NullMemoryIndex()
    return _MEMORY_INDEX


# ============================================================
# Legacy accessors (older code may import these)
# ============================================================

def get_memory_engine() -> Any:
    # alias: older modules might expect "engine"
    return get_memory_index()


def get_memory_store() -> Any:
    # alias: older modules might expect "store"
    return get_memory_index()


def reset_memory_index() -> None:
    """
    Optional helper: forces reload next call.
    Useful after GCS sync completes.
    """
    global _MEMORY_INDEX
    _MEMORY_INDEX = None
