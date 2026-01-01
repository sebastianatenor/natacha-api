# routes/system_restore_status.py

from fastapi import APIRouter
import service_main

router = APIRouter(tags=["system"])

@router.get("/system/restore/status")
def restore_status():
    """
    Exposes the cognitive restore state loaded at startup.
    SINGLE SOURCE OF TRUTH.
    """
    state = service_main.COGNITIVE_RESTORE

    return {
        "restored": bool(state.get("restored")),
        "state": state,
    }
