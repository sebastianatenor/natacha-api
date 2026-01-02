"""
/system/state
Estado del sistema VERIFICADO (AGENTE_VERAZ)

Fuente única de verdad runtime.
NO inferencias. NO memoria cognitiva interpretada.
"""

import os
import time
from fastapi import APIRouter

from ops.memory.canonical_state import memory_state

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/state")
def system_state():
    return {
        "status": "ok",
        "verified": True,
        "timestamp": time.time(),
        "runtime": {
            "cloud_run": bool(os.getenv("K_SERVICE")),
            "service": os.getenv("K_SERVICE"),
            "revision": os.getenv("K_REVISION"),
            "python": os.getenv("PYTHON_VERSION", "unknown"),
            "verified": True,
        },
        "semantic": {
            "verified": False,
            "state": "unknown",
            "loaded": False,
            "confidence": "unknown",
            "note": "semantic registry not implemented",
        },
        "memory": memory_state(),
    }
