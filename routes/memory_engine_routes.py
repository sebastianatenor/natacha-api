from typing import Optional, Dict, Any

from fastapi import APIRouter, Query

from memory_engine import (
    save_raw_memory,
    consolidate_memory,
    list_recent_memories,
    save_system_rule,
    db,
    COL_SYSTEM,
    COL_SUMMARY,
)

router = APIRouter(prefix="/memory/engine", tags=["memory-engine"])


@router.post("/raw")
def memory_raw(payload: Dict[str, Any]):
    """
    Guarda una memoria cruda normalizada.
    """
    memory_id = save_raw_memory(payload)
    return {"status": "raw_saved", "memory_id": memory_id}


@router.post("/consolidate")
def memory_consolidate(user_id: Optional[str] = None):
    """
    Consolida memorias (global o por usuario).
    """
    result = consolidate_memory(user_id=user_id)
    if not result:
        return {"status": "empty", "result": None}
    return {"status": "ok", "result": result}


@router.get("/recent")
def memory_recent(
    user_id: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    """
    Lista memorias crudas recientes (para debug o para que Natacha
    pueda leer el contexto más nuevo).
    """
    items = list_recent_memories(user_id=user_id, limit=limit)
    return {"count": len(items), "items": items}


@router.post("/system")
def memory_system(payload: Dict[str, Any]):
    """
    Guarda una regla de sistema (por ejemplo, protocolo de trabajo).
    """
    note = payload.get("note", "")
    version = payload.get("version", "v1")
    save_system_rule(note, version)
    return {"status": "system_saved", "version": version}


@router.get("/context_bundle")
def memory_context_bundle(
    user_id: Optional[str] = None,
    recent_limit: int = Query(20, ge=1, le=200),
    include_global_fallback: bool = True,
):
    """
    Devuelve un paquete de contexto listo para Natacha:

    - system_rule: regla de sistema principal (core-v1 por defecto)
    - summary: resumen consolidado por usuario (o global si no hay)
    - recent: memorias crudas recientes
    """
    key = user_id or "global"

    # 1) Summary específico del usuario o global
    summary_doc = db.collection(COL_SUMMARY).document(key).get()
    summary = summary_doc.to_dict() if summary_doc.exists else None

    # Fallback a "global" si no hay summary del usuario
    if not summary and include_global_fallback and key != "global":
        global_doc = db.collection(COL_SUMMARY).document("global").get()
        if global_doc.exists:
            summary = global_doc.to_dict()

    # 2) Regla de sistema principal (core-v1)
    system_doc = db.collection(COL_SYSTEM).document("core-v1").get()
    system_rule = system_doc.to_dict() if system_doc.exists else None

    # 3) Recientes
    recent_items = list_recent_memories(user_id=user_id, limit=recent_limit)

    return {
        "status": "ok",
        "user_id": user_id,
        "system_rule": system_rule,
        "summary": summary,
        "recent": {
            "count": len(recent_items),
            "items": recent_items,
        },
    }
