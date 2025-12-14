import os
import shutil
from datetime import datetime
from typing import Dict

from unified_core.memory_lazy import (
    is_memory_available,
    get_memory_path,
)

SNAPSHOT_DIR = "/tmp/memory_snapshots"


def rollback_memory(snapshot_name: str) -> Dict:
    """
    Rollback seguro de memoria NDJSON a un snapshot previo.
    """
    if not is_memory_available():
        return {
            "status": "error",
            "reason": "memory_not_available",
        }

    memory_path = get_memory_path()
    if not memory_path or not os.path.exists(memory_path):
        return {
            "status": "error",
            "reason": "memory_file_missing",
        }

    snapshot_path = os.path.join(SNAPSHOT_DIR, snapshot_name)

    if not os.path.exists(snapshot_path):
        return {
            "status": "error",
            "reason": "snapshot_not_found",
            "snapshot": snapshot_name,
        }

    # Backup previo al rollback
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    backup_path = f"{memory_path}.pre_rollback.{ts}.bak"
    shutil.copy2(memory_path, backup_path)

    # Rollback efectivo
    shutil.copy2(snapshot_path, memory_path)

    return {
        "status": "ok",
        "snapshot_restored": snapshot_name,
        "backup_created": os.path.basename(backup_path),
        "timestamp": ts,
    }
