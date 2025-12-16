# unified_core/memory_lazy.py
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class BaseMemoryIndex:
    """
    Base contract for ALL memory indexes.
    ensure_loaded exists ONLY for legacy compatibility.
    """
    store_loaded: bool = False

    def ensure_loaded(self) -> None:
        # Legacy no-op (DO NOT REMOVE)
        return

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        return []


class NullMemoryIndex(BaseMemoryIndex):
    pass


class NDJSONMemoryIndex(BaseMemoryIndex):
    def __init__(self, local_path: str):
        self.local_path = local_path
        self._cache: List[Dict[str, Any]] = []
        self.store_loaded = False
        self._load()

    def _load(self) -> None:
        try:
            p = Path(self.local_path)
            if not p.exists():
                self._cache = []
                self.store_loaded = False
                return

            items = []
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
        except Exception:
            self._cache = []
            self.store_loaded = False

    def list_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        if limit <= 0:
            return []
        return self._cache[-limit:]


_MEMORY_INDEX: Optional[BaseMemoryIndex] = None


def _build_index() -> BaseMemoryIndex:
    try:
        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        if Path(local_path).exists():
            return NDJSONMemoryIndex(local_path)
    except Exception:
        pass
    return NullMemoryIndex()


def get_memory_index() -> BaseMemoryIndex:
    global _MEMORY_INDEX
    if _MEMORY_INDEX is None:
        _MEMORY_INDEX = _build_index()
    return _MEMORY_INDEX


# 🔁 LEGACY ALIASES (NO BORRAR)
def get_memory_engine() -> BaseMemoryIndex:
    engine = _MEMORY_INDEX

    # 🔒 Garantía absoluta de interfaz
    if not hasattr(engine, "ensure_loaded") or not hasattr(engine, "list_recent"):
        return _SafeMemoryAdapter()

    return engine

def get_memory_store() -> BaseMemoryIndex:
    return get_memory_index()


def reset_memory_index() -> None:
    global _MEMORY_INDEX
    _MEMORY_INDEX = None

class _SafeMemoryAdapter:
    """
    Adapter final: garantiza interfaz mínima aunque no haya memoria real.
    """
    def ensure_loaded(self) -> None:
        return None

    def list_recent(self, limit: int = 20):
        return []

    def list_all(self):
        return []

    def add(self, *args, **kwargs):
        return None
