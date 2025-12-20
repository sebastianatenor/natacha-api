from datetime import datetime, timezone
from google.cloud import storage
import json
import os

from unified_core.memory_paths import get_canonical_memory_path

BUCKET = "natacha-memory-store"
SNAPSHOT_PREFIX = "snapshots"


def _today_key():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _snapshot_blob_name():
    return f"{SNAPSHOT_PREFIX}/{_today_key()}.jsonl"


def snapshot_exists_today(client):
    bucket = client.bucket(BUCKET)
    blob = bucket.blob(_snapshot_blob_name())
    return blob.exists()


def _write_timeline_event():
    """
    Indexa el snapshot diario en el timeline cognitivo.
    """
    path = get_canonical_memory_path()

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "kind": "cognitive_snapshot",
        "date": _today_key(),
        "revision": os.getenv("K_REVISION"),
        "confidence": "high",
    }

    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def write_daily_snapshot():
    try:
        client = storage.Client()

        if snapshot_exists_today(client):
            print("[SNAPSHOT] Daily snapshot already exists — skipping")
            return

        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "kind": "daily_snapshot",
            "revision": os.getenv("K_REVISION"),
            "semantic": None,
            "memory": None,
            "confidence": "high",
        }

        # Semantic state
        try:
            from ops.cognitive.state_registry import read_last_cognitive_state
            snapshot["semantic"] = read_last_cognitive_state("semantic")
        except Exception:
            snapshot["semantic"] = {"state": "unknown"}

        # Memory summary
        try:
            path = get_canonical_memory_path()
            snapshot["memory"] = {
                "items_count": sum(1 for _ in path.open("r", encoding="utf-8")),
                "path": str(path),
            }
        except Exception:
            snapshot["memory"] = {"state": "unknown"}

        data = json.dumps(snapshot, ensure_ascii=False) + "\n"

        bucket = client.bucket(BUCKET)
        blob = bucket.blob(_snapshot_blob_name())
        blob.upload_from_string(data, content_type="application/json")

        # 🔑 INDEXAR EN TIMELINE
        _write_timeline_event()

        print("[SNAPSHOT] Daily snapshot written + indexed")

    except Exception as e:
        print(f"[SNAPSHOT][WARN] {e}")
