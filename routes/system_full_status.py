# routes/system_full_status.py
from fastapi import APIRouter
from datetime import datetime
import os

from routes.system_state import get_system_state
from ops.memory.manager import user_context_manager

router = APIRouter(prefix="/ops/system", tags=["System"])

@router.get("/full_status")
def full_status(user_id: str | None = None):
    """
    Estado global del sistema (A+B).
    Modo A: siempre activo.
    Modo B: solo si NATACHA_SELF_EXTENDED=1
    """

    status = {
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "A",
        "system": get_system_state(),
    }

    if user_id:
        try:
            status["user_state"] = user_context_manager.snapshot(user_id)
        except Exception:
            status["user_state"] = "unavailable"

    # -------------------------
    # 🅱️ MODO B (EXTENDIDO)
    # -------------------------
    if os.getenv("NATACHA_SELF_EXTENDED") == "1":
        status["mode"] = "A+B"
        extended = {}

        # Introspección
        try:
            from ops.introspection.history_reader import read_history
            extended["introspection"] = read_history(limit=5)
        except Exception:
            extended["introspection"] = "not_loaded"

        # Evolución cognitiva
        try:
            from ops.cognitive_evolution import cognitive_status
            extended["cognitive_evolution"] = cognitive_status()
        except Exception:
            extended["cognitive_evolution"] = "not_loaded"

        status["extended"] = extended

    return status
