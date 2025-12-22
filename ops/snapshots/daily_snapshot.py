from datetime import datetime, timezone
import json
import os
import time

from google.cloud import storage

from unified_core.memory_paths import get_canonical_memory_path
from ops.cognitive.state_registry import read_last_cognitive_state
from ops.memory.persist import persist_memory


BUCKET = "natacha-memory-store"
SNAPSHOT_PREFIX = "snapshots"


def _today_key():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _snapshot_blob_name():
    return f"{SNAPSHOT_PREFIX}/{_today_key()}.jsonl"


def write_daily_snapshot(retries: int = 5, wait: float = 1.0):
    revision = os.getenv("K_REVISION")

    if not revision:
        print("[SNAPSHOT][WARN] K_REVISION not set")
        return

    path = get_canonical_memory_path()

    # Esperar a que la memoria canónica exista
    for _ in range(retries):
        if path.exists() and path.stat().st_size > 0:
            break
        time.sleep(wait)
    else:
        print("[SNAPSHOT][WARN] canonical memory not ready")
        return

    # --- Snapshot cognitivo
    semantic = read_last_cognitive_state("semantic") or {
        "state": "not_loaded",
        "confidence": "low"
    }

    snapshot_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "kind": "daily_snapshot",
        "revision": revision,
        "observed_state": {
            "semantic": semantic,
        },
        "confidence": "high",
    }

    # --- Append al memory_store (canónico local)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(snapshot_event, ensure_ascii=False) + "\n")

    print("[SNAPSHOT] daily_snapshot appended to canonical memory")

    # --- Persistir a GCS + backup completo
    try:
        client = storage.Client()
        bucket = client.bucket(BUCKET)

        blob = bucket.blob(_snapshot_blob_name())
        blob.upload_from_string(
            json.dumps(snapshot_event, ensure_ascii=False) + "\n",
            content_type="application/json",
        )

        persist_memory()

        print("[SNAPSHOT] daily snapshot + canonical memory stored in GCS")

    except Exception as e:
        print(f"[SNAPSHOT][WARN] GCS persistence failed: {e}")
