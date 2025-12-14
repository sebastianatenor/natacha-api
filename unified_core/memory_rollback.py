import os
from pathlib import Path
from google.cloud import storage


def rollback_memory(snapshot: str):
    """
    Restaura un snapshot de memoria desde GCS a /tmp/memory_store.jsonl
    Cloud Run safe.
    """

    if not snapshot.endswith(".jsonl"):
        return {
            "status": "error",
            "reason": "Invalid snapshot name"
        }

    bucket_name = "natacha-memory-store"
    local_path = "/tmp/memory_store.jsonl"

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(snapshot)

        if not blob.exists():
            return {
                "status": "error",
                "reason": f"Snapshot not found: {snapshot}"
            }

        blob.download_to_filename(local_path)

        return {
            "status": "ok",
            "snapshot": snapshot,
            "restored": True,
            "path": local_path
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }
