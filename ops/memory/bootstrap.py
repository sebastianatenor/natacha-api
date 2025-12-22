import os
from google.cloud import storage
from unified_core.memory_paths import get_canonical_memory_path

BUCKET = "natacha-memory-store"
BLOB_NAME = "memory_store.jsonl"


def bootstrap_memory():
    path = get_canonical_memory_path()

    client = storage.Client()
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(BLOB_NAME)

    if blob.exists():
        blob.download_to_filename(path)
        print("[BOOTSTRAP] memory_store.jsonl restored from GCS")
    else:
        print("[BOOTSTRAP] no remote memory found, starting fresh")
        path.touch(exist_ok=True)
