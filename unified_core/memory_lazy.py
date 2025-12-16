# unified_core/memory_lazy.py
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================
# MemoryIndex-like contract (LEGACY + v4 compatible)
# Required methods:
# - list_recent(limit)
# - ensure_loaded()
# - store_loaded (bool)
# ============================================================


class NullMemoryIndex:
    """
    Safe fallback that never crashes.
    Fully legacy-compatible.
    """
    store_loaded: bool = False

    def ensure_loaded(self) -> None:
        return

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return []


class NDJSONMemoryIndex:
    """
    Cloud Run safe memory index.
    Reads /tmp/memory_store.jsonl (synced async from GCS).
    """

    def __init__(self, local_path: str):
        self.local_path = local_path
        self.store_loaded: bool = False
        self._cache: List[Dict[str, Any]] = []
        self._loaded_once: bool = False

    def ensure_loaded(self) -> None:
        """
        LEGACY compatibility.
        Idempotent. Never throws.
        """
        if self._loaded_once:
            return
        self._load()

    def _load(self) -> None:
        try:
            p = Path(self.local_path)
            if not p.exists():
                self.store_loaded = False
                self._cache = []
                self._loaded_once = True
                return

            items: List[Dict[str, Any]] = []
            with p.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if isinstance(obj, dict):
                            items.append(obj)
                    except Exception:
                        continue

            self._cache = items
            self.store_loaded = True
            self._loaded_once = True

        except Exception:
            self.store_loaded = False
            self._cache = []
            self._loaded_once = True

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            self.ensure_loaded()
            if not self._cache or limit <= 0:
                return []
            return self._cache[-limit:]
        except Exception:
            return []


# ============================================================
# Lazy singleton accessor (Cloud Run safe)
# ============================================================

_MEMORY_INDEX: Optional[Any] = None


def _build_index() -> Any:
    try:
        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        if Path(local_path).exists():
            return NDJSONMemoryIndex(local_path)
    except Exception:
        pass
    return NullMemoryIndex()


def get_memory_index() -> Any:
    global _MEMORY_INDEX
    if _MEMORY_INDEX is None:
        _MEMORY_INDEX = _build_index()

    # HARD SAFETY
    if isinstance(_MEMORY_INDEX, dict):
        _MEMORY_INDEX = NullMemoryIndex()

    return _MEMORY_INDEX


# ============================================================
# Legacy aliases
# ============================================================

def get_memory_engine() -> Any:
    return get_memory_index()


def get_memory_store() -> Any:
    return get_memory_index()


def reset_memory_index() -> None:
    global _MEMORY_INDEX
    _MEMORY_INDEX = None
