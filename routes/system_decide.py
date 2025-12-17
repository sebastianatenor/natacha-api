# routes/system_decide.py

from fastapi import APIRouter
from typing import Dict, Any
import time

from ops.system.manifest_decider import ManifestDecider
from unified_core.memory_lazy import get_memory_index

router = APIRouter(
    prefix="/ops/system",
    tags=["system-decision"]
)

decider = ManifestDecider()


@router.get("/decide")
def system_decide() -> Dict[str, Any]:
    """
    Decisor ejecutivo PASIVO basado en manifiestos.

    - No ejecuta acciones
    - No modifica estado
    - No escribe memoria
    - Solo observa, razona y sugiere
    """

    now = time.time()

    # -------------------------------------------------
    # 1. Estado mínimo del sistema
    # -------------------------------------------------
    memory_index = get_memory_index()

    # Compatibilidad con motor NDJSON actual
    if hasattr(memory_index, "tail"):
        recent_events = memory_index.tail(limit=50)
    else:
        recent_events = []

    system_state = {
        "memory": {
            "items_count": memory_index.count()
        }
    }

    # -------------------------------------------------
    # 2. Evaluación cognitiva (manifiestos)
    # -------------------------------------------------
    suggestions = decider.evaluate(
        system_state=system_state,
        recent_context=recent_events,
        active_project=None
    )

    # -------------------------------------------------
    # 3. Respuesta
    # -------------------------------------------------
    return {
        "timestamp": now,
        "status": "ok",
        "mode": "passive-manifest-decision",
        "suggestions": [
            {
                "level": s.level,
                "title": s.title,
                "message": s.message,
                "source_manifest": s.source_manifest
            }
            for s in suggestions
        ]
    }
