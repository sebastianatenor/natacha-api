from typing import Dict, Any
from fastapi import APIRouter, Query, HTTPException

from unified_core.memory_reader_v2 import memory_reader_v2
from unified_core.memory_writer_v2 import memory_writer_v2

# --------------------------------------------------
# Router
# --------------------------------------------------
router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])


# --------------------------------------------------
# Endpoints (SAFE / LAZY / A2-COMPATIBLE)
# --------------------------------------------------
@router.get("/recent")
def memory_recent(
    limit: int = Query(20, ge=1, le=200),
):
    """
    Devuelve eventos recientes desde memoria unificada (read-only).
    """
    items = memory_reader_v2.load_recent(limit)
    return {
        "status": "ok",
        "engine": "memory_reader_v2",
        "count": len(items),
        "items": items,
    }


@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    """
    Inserta un evento crudo en memoria (safe write).
    """
    try:
        memory_id = memory_writer_v2.save_raw(payload)
        return {
            "status": "raw_saved",
            "memory_id": memory_id,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"memory write failed: {e}",
        )


# --------------------------------------------------
# Debug endpoint (SEGURO)
# --------------------------------------------------
@router.get("/_debug")
def debug_info():
    """
    Debug liviano para verificar estado del reader.
    """
    try:
        items = memory_reader_v2.load_recent(1)
        return {
            "reader": "ok",
            "sample_items": len(items),
        }
    except Exception as e:
        return {
            "reader": "error",
            "error": str(e),
        }
