import os
import time
from fastapi import APIRouter, Header, HTTPException

router = APIRouter()

DEBUG_SECRET = os.getenv("DEBUG_SECRET", "")
DEBUG_ENABLED = os.getenv("DEBUG_ENABLED", "false").lower() in ("1","true","yes","on")

def _check(secret_from_header: str | None):
    # Hide endpoints completely unless enabled
    if not DEBUG_ENABLED:
        raise HTTPException(status_code=404, detail="Not Found")
    # Require header to avoid misuse
    if not DEBUG_SECRET or secret_from_header != DEBUG_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

@router.get("/debug/boom")
def debug_boom(x_debug_secret: str | None = Header(default=None)):
    _check(x_debug_secret)
    # Force a 500 to test alerting
    raise HTTPException(status_code=500, detail="Forced error for alert test")

@router.get("/debug/sleep")
def debug_sleep(ms: int = 1000, x_debug_secret: str | None = Header(default=None)):
    _check(x_debug_secret)
    time.sleep(max(0, ms) / 1000.0)
    return {"slept_ms": ms}
