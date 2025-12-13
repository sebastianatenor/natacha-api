from fastapi import APIRouter
from typing import Dict, Any

from routes.system_state import system_state
from ops.system_interpreter import interpret_system_state

router = APIRouter(
    prefix="/ops/system",
    tags=["system-state"]
)


@router.get("/diagnose")
def system_diagnose() -> Dict[str, Any]:
    """
    Diagnóstico interpretado del sistema.
    Cloud Run aware:
    - Si semantic/memory están disponibles pero no cargados,
      intenta verificación lazy NO bloqueante.
    """

    raw_state = system_state()

    # --------------------------------------------------
    # 🔹 Lazy materialization (SAFE)
    # --------------------------------------------------

    try:
        # Semantic core: solo tocamos si hay token y no está cargado
        semantic = raw_state.get("semantic", {})
        if semantic.get("hf_token_present") and not semantic.get("loaded"):
            from unified_core.semantic_core import get_semantic_core
            core = get_semantic_core()
            core.ensure_loaded()
            semantic["loaded"] = True
    except Exception:
        pass  # Nunca romper diagnóstico

    try:
        # Memory: solo verificamos si el archivo ya está sincronizado
        memory = raw_state.get("memory", {})
        if not memory.get("store_loaded"):
            from unified_core.memory_lazy import memory_engine
            if memory_engine.store_available():
                memory_engine.ensure_loaded()
                memory["store_loaded"] = True
                memory["store_path"] = memory_engine.store_path
                memory["items_count"] = memory_engine.items_count
    except Exception:
        pass  # Diagnóstico siempre responde

    diagnosis = interpret_system_state(raw_state)

    return {
        "state": raw_state,
        "diagnosis": diagnosis
    }
