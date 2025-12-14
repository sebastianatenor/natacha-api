import os
import datetime
from google.cloud import storage

MEMORY_BUCKET = "natacha-memory-store"
MEMORY_FILE = "memory_store.jsonl"
BACKUP_PREFIX = "backups"


def create_memory_snapshot():
    """
    Crea un snapshot versionado de memory_store.jsonl en GCS.
    Cloud Run safe. No bloquea startup.
    """

    if os.getenv("K_SERVICE") is None:
        return {
            "status": "skipped",
            "reason": "Not running in Cloud Run"
        }

    client = storage.Client()
    bucket = client.bucket(MEMORY_BUCKET)

    source_blob = bucket.blob(MEMORY_FILE)

    if not source_blob.exists():
        return {
            "status": "error",
            "reason": "memory_store.jsonl not found in bucket"
        }

    timestamp = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"memory_{timestamp}.jsonl"
    destination_path = f"{BACKUP_PREFIX}/{snapshot_name}"

    bucket.copy_blob(
        source_blob,
        bucket,
        destination_path
    )

    return {
        "status": "ok",
        "snapshot": snapshot_name,
        "path": f"gs://{MEMORY_BUCKET}/{destination_path}"
    }
