from google.cloud import storage
from unified_core.memory_paths import get_canonical_memory_path

BUCKET = "natacha-memory-store"
BLOB_NAME = "memory_store.jsonl"


def persist_memory():
    path = get_canonical_memory_path()

    if not path.exists():
        print("[MEMORY] no canonical memory to persist")
        return

    client = storage.Client()
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(BLOB_NAME)

    blob.upload_from_filename(path)
    print("[MEMORY] canonical memory persisted to GCS")
