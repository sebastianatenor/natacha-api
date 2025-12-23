from fastapi import APIRouter
from datetime import datetime
import os

router = APIRouter(prefix="/ops/system", tags=["system"])


def get_baseline_internal():
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": os.getenv("K_SERVICE", "natacha-api"),
        "revision": os.getenv("K_REVISION"),
        "environment": "cloud_run" if os.getenv("K_SERVICE") else "local",
        "flags": {
            "COGNITIVE_FREEZE": os.getenv("COGNITIVE_FREEZE"),
            "NATACHA_FAST_BOOT": os.getenv("NATACHA_FAST_BOOT"),
        },
        "memory": {
            "canonical_path": os.getenv("NATACHA_MEMORY_LOCAL"),
            "expected": True,
        },
        "semantic": {
            "expected_loaded": False,
        },
        "confidence": "high",
    }


@router.get("/baseline")
def baseline():
    return {
        "status": "ok",
        "baseline": get_baseline_internal(),
        "confidence": "high",
    }
