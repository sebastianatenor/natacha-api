import os
import time
from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["internal"])

_last_warmup = 0
MIN_SECONDS_BETWEEN_WARMUPS = 300  # 5 minutos


@router.post("/__warmup")
def warmup_semantic_core():
    """
    Warmup protegido:
    - Solo si está habilitado
    - Rate-limited
    - Cloud Run safe
    """
    global _last_warmup

    if os.getenv("NATACHA_ENABLE_WARMUP", "false") != "true":
        raise HTTPException(status_code=403, detail="Warmup disabled")

    now = time.time()
    if now - _last_warmup < MIN_SECONDS_BETWEEN_WARMUPS:
        return {
            "status": "skipped",
            "message": "Warmup recently executed",
            "seconds_since_last": round(now - _last_warmup, 2)
        }

    start = time.time()

    from unified_core.semantic_core import get_semantic_core

    core = get_semantic_core()
    core.ensure_loaded()

    _last_warmup = time.time()

    return {
        "status": "ok",
        "message": "Semantic core warmed",
        "load_time_seconds": round(_last_warmup - start, 2)
    }
