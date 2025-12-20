from datetime import datetime, timezone
from google.cloud import storage
import json
import os

from unified_core.memory_paths import get_canonical_memory_path
from ops.cognitive.state_registry import write_cognitive_event

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


def write_daily_snapshot():
    try:
        client = storage.Client()

        if snapshot_exists_today(client):
            print("[SNAPSHOT] Daily snapshot already exists — skipping")
            return

        # ============================
        # Construir snapshot
        # ============================
        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "kind": "daily_snapshot",
            "revision": os.getenv("K_REVISION"),
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

        # ============================
        # Persistir en GCS
        # ============================
        data = json.dumps(snapshot, ensure_ascii=False) + "\n"
        bucket = client.bucket(BUCKET)
        blob = bucket.blob(_snapshot_blob_name())
        blob.upload_from_string(data, content_type="application/json")

        print("[SNAPSHOT] Daily snapshot written")

        # ============================
        # 🔥 INDEXAR EN TIMELINE 🔥
        # ============================
        write_cognitive_event(
            kind="daily_snapshot",
            subsystem="snapshot",
            state="written",
            confidence="high",
            details={
                "date": _today_key(),
                "gcs_path": _snapshot_blob_name(),
            },
        )

        print("[SNAPSHOT] Daily snapshot indexed into cognitive timeline")

    except Exception as e:
        print(f"[SNAPSHOT][WARN] {e}")
