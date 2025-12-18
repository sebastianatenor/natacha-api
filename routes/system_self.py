# routes/system_self.py
from fastapi import APIRouter
from datetime import datetime

from ops.system.self_model import build_self_model

router = APIRouter(prefix="/ops/system", tags=["System Self"])


@router.get("/self")
def system_self():
    """
    Read-only system self model.
    Describe cómo Natacha se entiende a sí misma en esta revisión.
    """
    model = build_self_model()
    return {
        "status": "ok",
        "engine": "system_self_model",
        "ts": datetime.utcnow().isoformat() + "Z",
        "self": model,
    }
