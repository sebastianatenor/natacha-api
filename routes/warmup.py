import os
import time
from fastapi import APIRouter, HTTPException

from unified_core.semantic_core import get_semantic_core

router = APIRouter(tags=["internal"])

# Rate limit global (proceso)
_last_warmup_ts = 0
MIN_SECONDS_BETWEEN_WARMUPS = 300  # 5 minutos


@router.post("/__warmup")
def warmup_semantic_core():
    """
    Warmup del Semantic Core (singleton real).
    - Cloud Run safe
    - Rate-limited
    - Estado consistente con system_state / diagnose
    """
    global _last_warmup_ts

    # Feature flag (seguridad)
    if os.getenv("NATACHA_ENABLE_WARMUP", "false") != "true":
        raise HTTPException(status_code=403, detail="Warmup disabled")

    now = time.time()

    # Rate limit
    if now - _last_warmup_ts < MIN_SECONDS_BETWEEN_WARMUPS:
        return {
            "status": "skipped",
            "message": "Warmup recently executed",
            "seconds_since_last": round(now - _last_warmup_ts, 2),
        }

    start = time.time()

    core = get_semantic_core()
    already_loaded = core.is_loaded()

    # Carga real (idempotente)
    core.ensure_loaded()

    _last_warmup_ts = time.time()

    return {
        "status": "ok",
        "message": "Semantic core warmed",
        "already_loaded": already_loaded,
        "loaded": core.is_loaded(),
        "load_time_seconds": round(_last_warmup_ts - start, 2),
    }
