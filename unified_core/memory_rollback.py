import os
from google.cloud import storage


BUCKET_NAME = "natacha-memory-store"
BACKUPS_PREFIX = "backups/"
LOCAL_MEMORY_PATH = "/tmp/memory_store.jsonl"


def rollback_memory(snapshot: str):
    """
    Restaura un snapshot de memoria desde GCS backups/.
    Cloud Run safe.
    """

    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET_NAME)

        # 🔑 Siempre buscamos en backups/
        blob_path = f"{BACKUPS_PREFIX}{snapshot}"
        blob = bucket.blob(blob_path)

        if not blob.exists():
            return {
                "status": "error",
                "reason": f"Snapshot not found in backups/: {snapshot}"
            }

        blob.download_to_filename(LOCAL_MEMORY_PATH)

        return {
            "status": "ok",
            "snapshot": snapshot,
            "restored": True,
            "path": LOCAL_MEMORY_PATH,
            "source": f"gs://{BUCKET_NAME}/{blob_path}"
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }
