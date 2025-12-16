import os
import json
import uuid
from typing import List, Dict, Any
from unified_core.semantic_core import get_semantic_core

# ===============================
# CONFIG
# ===============================

GCS_BUCKET = "natacha-memory-store"
GCS_VECTOR_PATH = "vector_memory.jsonl"
LOCAL_VECTOR_PATH = "/tmp/vector_memory.jsonl"

semantic_core = get_semantic_core()


# ===============================
# LAZY SYNC DESDE GCS
# ===============================

def ensure_vectorstore_synced():
    if os.path.exists(LOCAL_VECTOR_PATH):
        return

    try:
        from google.cloud import storage
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(GCS_VECTOR_PATH)

        if blob.exists():
            blob.download_to_filename(LOCAL_VECTOR_PATH)
            print("[VECTORSTORE] Synced vector_memory.jsonl from GCS")
        else:
            open(LOCAL_VECTOR_PATH, "w").close()
            print("[VECTORSTORE] No vector file in GCS, created empty")

    except Exception as e:
        print("[VECTORSTORE] Sync failed, running empty:", e)
        open(LOCAL_VECTOR_PATH, "w").close()


# ===============================
# VECTOR STORE
# ===============================

class VectorStore:
    def __init__(self, path: str = LOCAL_VECTOR_PATH):
        ensure_vectorstore_synced()
        self.path = path

    def add(self, text: str, meta: Dict[str, Any]):
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

    def load_all(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.path):
            return []

        items = []
        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except:
                    continue
        return items

    def similarity(self, v1, v2) -> float:
        import numpy as np
        v1 = np.array(v1)
        v2 = np.array(v2)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        semantic_core.ensure_loaded()
        q_vec = semantic_core._model.encode(query).tolist()

        items = self.load_all()
        if not items:
            return []

        ranked = []
        for item in items:
            score = self.similarity(q_vec, item.get("vector", []))
            ranked.append((score, item))

        ranked.sort(reverse=True, key=lambda x: x[0])
        return [x[1] for x in ranked[:top_k]]


# Singleton
vector_store = VectorStore()
