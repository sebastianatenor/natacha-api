import os
from typing import Optional

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
        """
        Store is available if:
        - already loaded OR
        - local file exists OR
        - remote GCS object exists
        """
        if self._loaded:
            return True

        if os.path.exists(self.local_path):
            return True

        # Remote check (GCS)
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
        """
        Load memory store lazily.
        Safe to call multiple times.
        """
        if self._loaded:
            return True

        try:
            from google.cloud import storage

            client = storage.Client()
            bucket = client.bucket(self.bucket_name)
            blob = bucket.blob(self.blob_name)

            blob.download_to_filename(self.local_path)

            self.store_path = self.local_path

            # Count items
            with open(self.local_path, "r", encoding="utf-8") as f:
                self.items_count = sum(1 for _ in f)

            self._loaded = True
            return True

        except Exception as e:
            print(f"[MEMORY][WARN] Failed to load memory: {e}")
            return False

    # ------------------------------------------------------------
    # BACKWARD COMPAT – requerido por context_engine_v4
    # ------------------------------------------------------------

    def get_memory_index():
        """
        Backward compatibility shim.
        Returns the default memory index if available,
        otherwise an empty structure.
        """
        try:
            from unified_core.memory_engine import memory_index
            return memory_index
        except Exception:
            return {}

# Singleton
memory_engine = MemoryLazyEngine()

