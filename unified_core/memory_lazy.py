import os
from typing import Optional

# ============================================================
# Memory Lazy Engine
# ============================================================

class MemoryLazyEngine:
    def __init__(self):
        self.store_path: Optional[str] = None
        self.items_count: int = 0
        self._loaded = False

        self.bucket_name = "natacha-memory-store"
        self.blob_name = "memory_store.jsonl"
        self.local_path = "/tmp/memory_store.jsonl"

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
    # Load (lazy, safe)
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

            self._loaded = True
            return True

        except Exception as e:
            print(f"[MEMORY][WARN] Failed to load memory: {e}")
            return False


# ============================================================
# Singleton
# ============================================================

memory_engine = MemoryLazyEngine()

# ============================================================
# 🔙 BACKWARD COMPATIBILITY LAYER (CRÍTICO)
# ============================================================

def get_memory_engine():
    """
    Legacy accessor.
    Returns the singleton memory engine.
    """
    return memory_engine


def get_memory_index():
    """
    Legacy accessor used by context_engine_v4 and others.
    Returns memory_index if present, otherwise empty dict.
    """
    try:
        from unified_core.memory_engine import memory_index
        return memory_index
    except Exception:
        return {}
