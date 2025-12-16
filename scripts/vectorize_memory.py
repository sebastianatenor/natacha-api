import json
from unified_core.memory_lazy import get_memory_index
from unified_core.vectorstore.store import vector_store
from google.cloud import storage

GCS_BUCKET = "natacha-memory-store"
GCS_PATH = "vector/vector_memory.jsonl"
LOCAL_PATH = "/tmp/vector_memory.jsonl"


def vectorize_memory(limit: int = 500):
    memory = get_memory_index()
    items = memory.list_recent(limit=limit)

    print(f"[VECTORIZE] Vectorizing {len(items)} items")

    # Limpiamos archivo local
    open(LOCAL_PATH, "w").close()

    for item in items:
        text = item.get("text", "")
        if not text:
            continue

        meta = {
            "tags": item.get("tags", []),
            "timestamp": item.get("meta", {}).get("timestamp"),
        }

        vector_store.add(text=text, meta=meta)

    # Subir a GCS (MISMO PATH que usa VectorStore)
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)
    blob = bucket.blob(GCS_PATH)

    blob.upload_from_filename(LOCAL_PATH)
    print(f"[VECTORIZE] Uploaded vectorstore to gs://{GCS_BUCKET}/{GCS_PATH}")


if __name__ == "__main__":
    vectorize_memory()
