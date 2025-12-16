import os
from typing import Optional, List


# =============================================================
# NULL SAFE MEMORY INDEX (NO ROMPE CONTEXT ENGINE)
# =============================================================

class NullMemoryIndex:
    store_loaded = False

    def list_recent(self, limit: int = 20) -> List[dict]:
        return []


# =============================================================
# LAZY MEMORY ENGINE
# =============================================================

class MemoryLazyEngine:
    def __init__(self):
        self.store_path: Optional[str] = None
        self.items_count: int = 0
        self._loaded = False

        self.bucket_name = "natacha-memory-store"
        self.blob_name = "memory_store.jsonl"
        self.local_path = "/tmp/memory_store.jsonl"

        self._memory_index = NullMemoryIndex()

    # --------------------------------------------------
    # Availability
    # --------------------------------------------------

    def store_available(self) -> bool:
        if self._loaded:
            return True

        if os.path.exists(self.local_path):
            return True

        try:
            from google.cloud import storage
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)
            return blob.exists()
        except Exception:
            return False

    # --------------------------------------------------
    # Load
    # --------------------------------------------------

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

            # Lazy import real engine
            try:
                from unified_core.memory_engine import memory_index
                self._memory_index = memory_index
            except Exception:
                self._memory_index = NullMemoryIndex()

            self._loaded = True
            return True

        except Exception as e:
            print(f"[MEMORY][WARN] Failed to load memory: {e}")
            self._memory_index = NullMemoryIndex()
            return False

    # --------------------------------------------------
    # PUBLIC API (STABLE)
    # --------------------------------------------------

    @property
    def store_loaded(self) -> bool:
        return self._loaded

    def list_recent(self, limit: int = 20):
        if not self._loaded:
            self.ensure_loaded()
        return self._memory_index.list_recent(limit=limit)


# =============================================================
# SINGLETON + LEGACY ADAPTERS
# =============================================================

memory_engine = MemoryLazyEngine()


def get_memory_index():
    """
    Legacy adapter required by context_engine_v4.
    ALWAYS returns an object with list_recent().
    """
    return memory_engine
