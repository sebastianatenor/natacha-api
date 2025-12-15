import os
from fastapi import HTTPException

LEGACY_WRITE_DISABLED = os.getenv("LEGACY_MEMORY_WRITE", "disabled") == "disabled"

def block_legacy_write():
    if LEGACY_WRITE_DISABLED:
        raise HTTPException(
            status_code=410,
            detail="Legacy memory write is disabled. Use /memory/v2/* endpoints."
        )
