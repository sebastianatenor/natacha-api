import json
from datetime import datetime
from google.cloud import storage
import os

BUCKET_NAME = os.getenv("GCS_BUCKET", "natacha-memory-store")
STATE_FILE = "adaptive_state.json"
LOCAL_PATH = f"/app/{STATE_FILE}"

def upload_state():
    """Sube el estado afectivo local a GCS."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(STATE_FILE)
    blob.upload_from_filename(LOCAL_PATH)
    return {"status": "uploaded", "time": datetime.utcnow().isoformat()}

def download_state():
    """Descarga el estado afectivo más reciente desde GCS."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(STATE_FILE)
    if blob.exists():
        blob.download_to_filename(LOCAL_PATH)
        return {"status": "downloaded", "time": datetime.utcnow().isoformat()}
    return {"status": "not_found"}

def ensure_state_file():
    """Crea un estado vacío si no existe localmente."""
    if not os.path.exists(LOCAL_PATH):
        with open(LOCAL_PATH, "w") as f:
            json.dump({"timeline": [], "last_update": datetime.utcnow().isoformat()}, f)
