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
    - Siempre devuelve JSON válido
    """

    now = time.time()

    # -------------------------------------------------
    # 1. Estado mínimo del sistema (SAFE)
    # -------------------------------------------------
    try:
        memory_index = get_memory_index()

        # NDJSONMemoryIndex no garantiza API rica
        items_count = getattr(memory_index, "items_count", None)
        if items_count is None:
            try:
                # fallback seguro: len del store interno si existe
                items_count = len(getattr(memory_index, "store", []))
            except Exception:
                items_count = None

        system_state = {
            "memory": {
                "loaded": memory_index is not None,
                "items_count": items_count
            }
        }

        recent_context = []  # PASIVO: no dependemos de eventos

    except Exception as e:
        system_state = {
            "memory": {
                "loaded": False,
                "error": str(e)
            }
        }
        recent_context = []

    # -------------------------------------------------
    # 2. Evaluación cognitiva (manifiestos)
    # -------------------------------------------------
    try:
        suggestions = decider.evaluate(
            system_state=system_state,
            recent_context=recent_context,
            active_project=None
        )
    except Exception as e:
        suggestions = [{
            "level": "warning",
            "title": "Manifest decider fallback",
            "message": f"Decider error capturado: {str(e)}",
            "source_manifest": "system_safety"
        }]

    # -------------------------------------------------
    # 3. Respuesta FINAL (nunca rompe)
    # -------------------------------------------------
    return {
        "timestamp": now,
        "status": "ok",
        "mode": "passive-manifest-decision",
        "system_state": system_state,
        "suggestions": [
            {
                "level": s.level if hasattr(s, "level") else s.get("level"),
                "title": s.title if hasattr(s, "title") else s.get("title"),
                "message": s.message if hasattr(s, "message") else s.get("message"),
                "source_manifest": (
                    s.source_manifest
                    if hasattr(s, "source_manifest")
                    else s.get("source_manifest")
                )
            }
            for s in suggestions
        ]
    }
