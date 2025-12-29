from google.cloud import storage
from ops.timeline.utils import get_timeline_path

BUCKET_NAME = "natacha-memory-store"
OBJECT_NAME = "timeline.jsonl"


def sync_timeline_to_gcs():
    """
    Sube el timeline local (/tmp) al bucket GCS.
    Se llama después de escribir eventos.
    """
    path = get_timeline_path()

    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(OBJECT_NAME)

    blob.upload_from_filename(path)
