import os
from google.cloud import storage

BUCKET_NAME = "natacha-memory-store"
LOCAL_PATH = "/tmp/memory_store.jsonl"


def rollback_memory(snapshot_name: str):
    """
    Restaura un snapshot de memoria desde GCS.
    Prioriza gs://bucket/backups/, fallback a raíz del bucket.
    Cloud Run safe.
    """

    if os.getenv("K_SERVICE") is None:
        return {
            "status": "error",
            "reason": "Rollback only allowed in Cloud Run"
        }

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)

    candidates = [
        f"backups/{snapshot_name}",
        snapshot_name,  # backward compatibility
    ]

    blob = None
    used_path = None

    for path in candidates:
        b = bucket.blob(path)
        if b.exists():
            blob = b
            used_path = path
            break

    if blob is None:
        return {
            "status": "error",
            "reason": f"Snapshot not found: {snapshot_name}"
        }

    blob.download_to_filename(LOCAL_PATH)

    return {
        "status": "ok",
        "snapshot": snapshot_name,
        "restored": True,
        "path": LOCAL_PATH,
        "source": f"gs://{BUCKET_NAME}/{used_path}"
    }
