"""
memory_lazy.py — Unified Memory Engine (FINAL)

- Single source of truth for memory
- Lazy load
- Cloud Run safe
- NDJSON backed
"""

from pathlib import Path
import json

_MEMORY = None


class UnifiedMemory:
    def __init__(self, store_path: str):
        self.store_path = Path(store_path)
        self._items = None

    def _load(self):
        if self._items is not None:
            return

        self._items = []
        if not self.store_path.exists():
            return

        with self.store_path.open() as f:
            for line in f:
                try:
                    self._items.append(json.loads(line))
                except Exception:
                    continue

    # -------- API usada por routes --------

    def list_recent(self, user_id=None, limit=20):
        self._load()
        items = self._items or []
        if user_id:
            items = [i for i in items if i.get("user_id") == user_id]
        return list(reversed(items))[:limit]

    def save_raw(self, payload):
        self._load()
        self._items.append(payload)
        return len(self._items)

    def consolidate(self, user_id=None):
        self._load()
        return {"count": len(self._items)}

    def save_system_rule(self, note, version):
        return {"version": version, "note": note}

    def build_context_bundle(self, **kwargs):
        self._load()
        return {
            "status": "ok",
            "engine": "memory_unified",
            "count": len(self._items),
            "items": self._items[-20:],
        }


def get_memory_index():
    global _MEMORY

    if _MEMORY is None:
        _MEMORY = UnifiedMemory("/tmp/memory_store.jsonl")

    return _MEMORY
