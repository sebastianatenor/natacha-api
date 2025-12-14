import os
import json
from datetime import datetime
from pathlib import Path

from unified_core.memory_lazy import get_memory_path, is_memory_available

SNAPSHOT_DIR = "/tmp/memory_snapshots"
MAX_LOCAL_SNAPSHOTS = 3  # rotación local segura


def ensure_snapshot_dir():
    Path(SNAPSHOT_DIR).mkdir(parents=True, exist_ok=True)


def create_snapshot(reason: str = "auto") -> dict:
    """
    Crea un snapshot local de la memoria activa.
    Cloud Run safe: NO bloquea startup.
    """
    if not is_memory_available():
        return {"status": "skipped", "reason": "memory_not_available"}

    memory_path = get_memory_path()
    if not memory_path or not os.path.exists(memory_path):
        return {"status": "skipped", "reason": "memory_file_missing"}

    ensure_snapshot_dir()

    ts = datetime.utcnow().isoformat().replace(":", "-")
    snapshot_name = f"snapshot_{ts}.jsonl"
    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)

    with open(memory_path, "r") as src, open(snapshot_path, "w") as dst:
        dst.write(src.read())

    _rotate_snapshots()

    return {
        "status": "ok",
        "snapshot": snapshot_name,
        "reason": reason,
        "created_at": ts,
    }


def _rotate_snapshots():
    snaps = sorted(Path(SNAPSHOT_DIR).glob("snapshot_*.jsonl"))
    if len(snaps) <= MAX_LOCAL_SNAPSHOTS:
        return

    for old in snaps[:-MAX_LOCAL_SNAPSHOTS]:
        try:
            old.unlink()
        except Exception:
            pass
