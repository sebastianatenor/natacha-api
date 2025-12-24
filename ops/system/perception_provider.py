# ops/system/perception_provider.py
import os
from datetime import datetime
from typing import Dict, Any, Optional

from ops.timeline.reader import read_events


def read_system_perception() -> Optional[Dict[str, Any]]:
    """
    Fuente única de percepción del sistema.
    B6.1: permite simular drift vía ENV VAR.
    """

    try:
        # -----------------------------
        # FLAGS
        # -----------------------------
        simulate_memory_missing = os.getenv("SIMULATE_MEMORY_MISSING") == "1"

        # -----------------------------
        # MEMORY
        # -----------------------------
        memory_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")

        memory_exists = os.path.exists(memory_path)

        if simulate_memory_missing:
            memory_exists = False  # 👈 DRIFT ARTIFICIAL

        memory_info = {
            "canonical_path": memory_path,
            "exists": memory_exists,
            "size_bytes": os.path.getsize(memory_path) if memory_exists else 0,
        }

        # -----------------------------
        # SEMANTIC (CANONICAL – state registry)
        # -----------------------------
        semantic_loaded = False
        try:
            from ops.cognitive.state_registry import read_last_cognitive_state

            semantic_state = read_last_cognitive_state("semantic")
            semantic_loaded = semantic_state.get("state") == "loaded"
        except Exception:
            semantic_loaded = False

        # -----------------------------
        # TIMELINE
        # -----------------------------
        events = read_events()
        last_event = events[-1] if events else None

        # -----------------------------
        # PERCEPTION OBJECT
        # -----------------------------
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": os.getenv("K_SERVICE", "natacha-api"),
            "revision": os.getenv("K_REVISION"),
            "project": None,
            "environment": "cloud_run" if os.getenv("K_SERVICE") else "local",
            "flags": {
                "COGNITIVE_FREEZE": os.getenv("COGNITIVE_FREEZE"),
                "NATACHA_FAST_BOOT": os.getenv("NATACHA_FAST_BOOT"),
                "SIMULATE_MEMORY_MISSING": simulate_memory_missing,
            },
            "memory": memory_info,
            "semantic": {
                "loaded": semantic_loaded,
            },
            "timeline": {
                "events_total": len(events),
                "last_event": last_event,
            },
        }

    except Exception as e:
        return {
            "error": "perception_failed",
            "detail": str(e),
        }
