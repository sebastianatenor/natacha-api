# unified_core/memory_lazy.py

import json
import os
from typing import Optional, List, Dict, Any

MEMORY_STORE_PATH = "/tmp/memory_store.jsonl"


class MemoryLazyIndex:
    """
    Lazy-loaded unified memory engine.
    Loads the NDJSON memory store only when first accessed.
    """

    def __init__(self):
        self._items: Optional[List[Dict[str, Any]]] = None
        self.store_loaded: bool = False
        self.store_path: Optional[str] = None

    # --------------------------------------------------
    # Internal loader
    # --------------------------------------------------
    def _load(self):
        if self._items is not None:
            return

        if not os.path.exists(MEMORY_STORE_PATH):
            raise RuntimeError(f"Memory store not found at {MEMORY_STORE_PATH}")

        items: List[Dict[str, Any]] = []
        with open(MEMORY_STORE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                items.append(json.loads(line))

        self._items = items
        self.store_loaded = True
        self.store_path = MEMORY_STORE_PATH

    # --------------------------------------------------
    # 🔹 NUEVO: método seguro para health / state
    # --------------------------------------------------
    def ensure_loaded(self) -> bool:
        """
        Ensures the memory store is loaded.
        Safe to call multiple times.
        """
        try:
            self._load()
            return True
        except Exception:
            return False

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
    def list_recent(self, user_id: Optional[str] = None, limit: int = 20):
        self._load()
        return list(reversed(self._items))[:limit]

    def save_raw(self, payload: Dict[str, Any]):
        self._load()
        self._items.append(payload)
        return payload.get("_id")

    def consolidate(self, user_id: Optional[str] = None):
        self._load()
        return {"count": len(self._items)}

    def build_context_bundle(
        self,
        user_id: Optional[str],
        recent_limit: int,
        include_global_fallback: bool = True,
    ):
        self._load()
        return {
            "status": "ok",
            "engine": "memory_unified",
            "user_id": user_id,
            "recent": {
                "count": min(len(self._items), recent_limit),
                "items": list(reversed(self._items))[:recent_limit],
            },
        }


# --------------------------------------------------
# Singleton accessor
# --------------------------------------------------
_memory_index: Optional[MemoryLazyIndex] = None


def get_memory_index() -> MemoryLazyIndex:
    global _memory_index
    if _memory_index is None:
        _memory_index = MemoryLazyIndex()
    return _memory_index
