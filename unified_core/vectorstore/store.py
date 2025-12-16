import os
import json
import uuid
from typing import List, Dict, Any

from google.cloud import storage
from unified_core.semantic_core import get_semantic_core

# Singleton semantic core (existing behavior)
semantic_core = get_semantic_core()

GCS_BUCKET = "natacha-memory-store"
GCS_PATH = "vector/vector_memory.jsonl"
LOCAL_PATH = "/tmp/vector_memory.jsonl"


class VectorStore:
    def __init__(self):
        self.path = LOCAL_PATH
        self._loaded = False

        # Guarantee attribute exists
        self.semantic_core = semantic_core

    def ensure_loaded(self):
        """
        Compatibility shim.
        Context engine expects vector_store.ensure_loaded().

        Safe + idempotent:
        - loads vectors from GCS once
        - ensures semantic model is ready
        """
        self._load_from_gcs()

        try:
            if hasattr(self.semantic_core, "ensure_loaded"):
                self.semantic_core.ensure_loaded()
            else:
                semantic_core.ensure_loaded()
        except Exception:
            return

    def _load_from_gcs(self):
        if self._loaded:
            return

        try:
            client = storage.Client()
            bucket = client.bucket(GCS_BUCKET)
            blob = bucket.blob(GCS_PATH)

            if not blob.exists():
                print("[VECTORSTORE] No vector file in GCS, starting empty")
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                open(self.path, "w").close()
                self._loaded = True
                return

            blob.download_to_filename(self.path)
            print("[VECTORSTORE] Loaded vectorstore from GCS")
            self._loaded = True

        except Exception as e:
            print(f"[VECTORSTORE] Could not load from GCS ({e}). Starting empty.")
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            if not os.path.exists(self.path):
                open(self.path, "w").close()
            self._loaded = True

    def load_all(self) -> List[Dict[str, Any]]:
        self._load_from_gcs()

        items: List[Dict[str, Any]] = []
        if not os.path.exists(self.path):
            return items

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    continue
        return items

    def add(self, text: str, meta: Dict[str, Any]):
        self._load_from_gcs()

        semantic_core.ensure_loaded()
        vector = semantic_core._model.encode(text).tolist()

        entry = {
            "id": uuid.uuid4().hex,
            "text": text,
            "meta": meta,
            "vector": vector,
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def add_documents(self, docs: List[Dict[str, Any]]):
        """
        Batch add helper.
        Expected format:
        {
            "text": "...",
            "meta": {...}
        }
        """
        added = 0

        for doc in docs:
            text = doc.get("text")
            meta = doc.get("meta", {})

            if not text:
                continue

            self.add(text=text, meta=meta)
            added += 1

        print(f"[VECTORSTORE] Added {added} documents")
        return added

    def similarity(self, v1, v2) -> float:
        import numpy as np

        v1 = np.array(v1)
        v2 = np.array(v2)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def search(self, query: str, top_k: int = 5):
        self._load_from_gcs()

        semantic_core.ensure_loaded()
        q_vec = semantic_core._model.encode(query).tolist()

        items = self.load_all()
        ranked = []

        for item in items:
            score = self.similarity(q_vec, item["vector"])
            ranked.append((score, item))

        ranked.sort(reverse=True, key=lambda x: x[0])
        return [x[1] for x in ranked[:top_k]]


vector_store = VectorStore()
