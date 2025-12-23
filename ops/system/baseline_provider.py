# ops/system/baseline_provider.py

import os
from datetime import datetime
from typing import Dict, Any


BASELINE: Dict[str, Any] | None = None


def build_baseline() -> Dict[str, Any]:
    """
    Construye el baseline cognitivo canónico del sistema.
    Se ejecuta una vez por revisión.
    """
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "natacha-api",
        "revision": os.getenv("K_REVISION"),
        "environment": os.getenv("ENVIRONMENT", "cloud_run"),
        "flags": {
            "COGNITIVE_FREEZE": os.getenv("COGNITIVE_FREEZE"),
            "NATACHA_FAST_BOOT": os.getenv("NATACHA_FAST_BOOT"),
        },
        "memory": {
            "canonical_path": "/tmp/memory_store.jsonl",
            "expected": True,
        },
        "semantic": {
            "expected_loaded": os.getenv("NATACHA_SEMANTIC_STARTUP") == "1",
        },
        "confidence": "high",
    }


def ensure_baseline() -> Dict[str, Any]:
    global BASELINE
    if BASELINE is None:
        BASELINE = build_baseline()
    return BASELINE


def read_baseline() -> Dict[str, Any]:
    return ensure_baseline()
