import json
from datetime import datetime, timezone
from unified_core.memory_paths import get_canonical_memory_path
from google.cloud import storage


def write_canonical_event(meta: dict, tags: list[str]):
    record = {
        "id": meta.get("id"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "meta": meta,
        "tags": tags,
    }

    path = get_canonical_memory_path()
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Persistencia en GCS
    if path.as_posix().startswith("/tmp"):
        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")
        blob.upload_from_filename(path)

    return record
