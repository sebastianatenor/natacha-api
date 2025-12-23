# ops/cognitive/repair_executor.py
import os
from pathlib import Path
from google.cloud import storage


def execute_repair(drift: dict) -> dict:
    """
    Ejecuta reparaciones SOLO si el sistema está armado.
    B6.2: solo soporta reparación de memoria.
    """

    if os.getenv("SELF_REPAIR_ARMED") != "1":
        return {
            "status": "blocked",
            "detail": "Self-repair not armed",
        }

    # ----------------------------------
    # MEMORY REPAIR
    # ----------------------------------
    if drift.get("memory_expected") and not drift.get("memory_exists"):
        try:
            local_path = Path(os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl"))

            client = storage.Client()
            bucket = client.bucket("natacha-memory-store")
            blob = bucket.blob("memory_store.jsonl")

            if not blob.exists():
                return {
                    "status": "failed",
                    "detail": "Canonical memory not found in GCS",
                }

            blob.download_to_filename(local_path)

            return {
                "status": "executed",
                "action": "restore_memory",
                "path": str(local_path),
            }

        except Exception as e:
            return {
                "status": "failed",
                "detail": str(e),
            }

    return {
        "status": "noop",
        "detail": "No executable repair for this drift",
    }
