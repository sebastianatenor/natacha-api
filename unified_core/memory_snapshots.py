import os
from datetime import datetime
from typing import List

def list_memory_snapshots() -> dict:
    """
    Lista snapshots reales de memoria desde GCS (bucket backups).
    Cloud Run safe. No toca memoria activa.
    """

    # Solo en Cloud Run
    if os.getenv("K_SERVICE") is None:
        return {
            "status": "error",
            "reason": "Snapshots listing only available in Cloud Run"
        }

    try:
        from google.cloud import storage

        bucket_name = "natacha-memory-store"
        prefix = "backups/"

        client = storage.Client()
        bucket = client.bucket(bucket_name)

        blobs = bucket.list_blobs(prefix=prefix)

        snapshots: List[dict] = []

        for blob in blobs:
            name = blob.name.replace(prefix, "")
            if not name.endswith(".jsonl"):
                continue

            snapshots.append({
                "name": name,
                "size_bytes": blob.size,
                "updated": blob.updated.isoformat() if blob.updated else None,
            })

        # Ordenar por fecha (más nuevo primero)
        snapshots.sort(
            key=lambda x: x["updated"] or "",
            reverse=True
        )

        return {
            "status": "ok",
            "count": len(snapshots),
            "snapshots": snapshots
        }

    except Exception as e:
        return {
            "status": "error",
            "reason": str(e)
        }
