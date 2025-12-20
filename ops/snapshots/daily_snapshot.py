from datetime import datetime, timezone
from google.cloud import storage
import json
import os

from unified_core.memory_paths import get_canonical_memory_path
from ops.cognitive.state_registry import write_cognitive_state, read_last_cognitive_state

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
            return {"status": "ok", "detail": "snapshot already exists"}

        # --------------------------------------------------
        # Construir snapshot
        # --------------------------------------------------
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

        # --------------------------------------------------
        # Persistir snapshot en GCS
        # --------------------------------------------------
        bucket = client.bucket(BUCKET)
        blob = bucket.blob(_snapshot_blob_name())
        blob.upload_from_string(
            json.dumps(snapshot, ensure_ascii=False) + "\n",
            content_type="application/json",
        )

        # --------------------------------------------------
        # 🔐 Indexar en Cognitive Timeline (CANÓNICO)
        # --------------------------------------------------
        write_cognitive_state(
            subsystem="snapshot",
            state="written",
            revision=os.getenv("K_REVISION"),
            confidence="high",
            details={
                "date": _today_key(),
                "bucket": BUCKET,
                "blob": _snapshot_blob_name(),
            },
        )

        print("[SNAPSHOT] Daily snapshot written & indexed")
        return {"status": "ok", "detail": "daily snapshot written"}

    except Exception as e:
        print(f"[SNAPSHOT][ERROR] {e}")
        return {"status": "error", "detail": str(e)}
