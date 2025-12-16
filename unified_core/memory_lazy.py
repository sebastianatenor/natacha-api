import os
from typing import Optional, List, Any


# =============================================================
# Lazy Memory Engine (Cloud Run safe)
# =============================================================

class MemoryLazyEngine:
    def __init__(self):
        self.store_path: Optional[str] = None
        self.items_count: int = 0
        self._loaded = False

        self.bucket_name = "natacha-memory-store"
        self.blob_name = "memory_store.jsonl"
        self.local_path = "/tmp/memory_store.jsonl"

    # ---------------------------------------------------------
    # Load (non-blocking friendly)
    # ---------------------------------------------------------

    def ensure_loaded(self) -> bool:
        if self._loaded:
            return True

        try:
            from google.cloud import storage

            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)

            blob.download_to_filename(self.local_path)
            self.store_path = self.local_path

            with open(self.local_path, "r", encoding="utf-8") as f:
                self.items_count = sum(1 for _ in f)

            self._loaded = True
            return True

        except Exception as e:
            print(f"[MEMORY][WARN] Lazy load failed: {e}")
            return False

    @property
    def store_loaded(self) -> bool:
        return self._loaded


# =============================================================
# Adapter (EXPECTED BY context_engine_v4)
# =============================================================

class MemoryIndexAdapter:
    def __init__(self, raw_index):
        self._index = raw_index

    @property
    def store_loaded(self) -> bool:
        return True

    def list_recent(self, limit: int = 20) -> List[Any]:
        try:
            items = list(self._index.values())
            return items[-limit:]
        except Exception:
            return []


# =============================================================
# Singleton
# =============================================================

memory_engine = MemoryLazyEngine()


# =============================================================
# Public API (SAFE IMPORTS)
# =============================================================

def get_memory_engine() -> MemoryLazyEngine:
    return memory_engine


def get_memory_index():
    """
    Returns an adapter compatible with ContextEngineV4.
    NEVER returns raw dict.
    """
    try:
        from unified_core.memory_engine import memory_index
        return MemoryIndexAdapter(memory_index)
    except Exception:
        return MemoryIndexAdapter({})
