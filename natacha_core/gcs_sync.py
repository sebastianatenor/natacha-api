"""
☁️ gcs_sync.py
Utilidad genérica para sincronizar la línea temporal emocional y reflexiones con Google Cloud Storage.
"""

import subprocess, datetime, os

BUCKET_PATH = "gs://natacha-memory-store/affective_timeline.jsonl"
LOCAL_PATH = "data/emotional_timeline.jsonl"

def sync_to_gcs():
    """Sube el archivo local a GCS si gsutil está disponible."""
    if not os.path.exists(LOCAL_PATH):
        return {"status": "no_local_file"}
    try:
        subprocess.run(
            ["gsutil", "cp", LOCAL_PATH, BUCKET_PATH],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {
            "status": "synced",
            "bucket": BUCKET_PATH,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def load_from_gcs():
    """Descarga la última versión desde GCS si existe."""
    try:
        subprocess.run(
            ["gsutil", "cp", BUCKET_PATH, LOCAL_PATH],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {"status": "downloaded", "file": LOCAL_PATH}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
