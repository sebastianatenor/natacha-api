from typing import Optional, Dict, Any
from datetime import datetime  # ⬅️ nuevo, para meta.generated_at

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

# ⬇️ Nuevo: integración con memoria semántica v2
from natacha_core import semantic_memory_v2


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
    project: Optional[str] = None,  # ⬅️ nuevo: para meta.project y futuras fuentes
    recent_limit: int = Query(20, ge=1, le=200),
    include_global_fallback: bool = True,
    # ⬇️ Parámetros opcionales para memoria semántica v2
    semantic_project: Optional[str] = None,
    semantic_q: Optional[str] = None,
    semantic_limit: int = Query(5, ge=1, le=50),
):
    """
    Devuelve un paquete de contexto listo para Natacha.

    Contrato v2 (REGISTRY.md):

    - summary: objeto con summary, highlights, next_steps
    - sources: semantic_v2, tasks, recent, etc.
    - meta: user_id, project, generated_at, engine_version

    Además mantiene campos legacy:
    - system_rule
    - recent
    - semantic_v2
    """
    key = user_id or "global"

    # 1) Summary específico del usuario o global
    summary_doc = db.collection(COL_SUMMARY).document(key).get()
    summary_data = summary_doc.to_dict() if summary_doc.exists else None

    # Fallback a "global" si no hay summary del usuario
    if not summary_data and include_global_fallback and key != "global":
        global_doc = db.collection(COL_SUMMARY).document("global").get()
        if global_doc.exists:
            summary_data = global_doc.to_dict()

    if summary_data is None:
        summary_data = {}

    # 2) Regla de sistema principal (core-v1)
    system_doc = db.collection(COL_SYSTEM).document("core-v1").get()
    system_rule = system_doc.to_dict() if system_doc.exists else None

    # 3) Recientes (memoria corta)
    recent_items = list_recent_memories(user_id=user_id, limit=recent_limit)
    recent_block = {
        "count": len(recent_items),
        "items": recent_items,
    }

    # 4) Bloque de memoria semántica v2 (opcional)
    semantic_block: Dict[str, Any] = {
        "status": "disabled",
        "reason": "No semantic_project or semantic_q provided.",
        "params": {
            "user_id": user_id,
            "project": semantic_project,
            "q": semantic_q,
            "limit": semantic_limit,
        },
        "result": None,
    }

    if semantic_project and semantic_q:
        try:
            sem_result = semantic_memory_v2.summarize(
                user_id=user_id,
                project=semantic_project,
                q=semantic_q,
                limit=semantic_limit,
            )
            semantic_block = {
                "status": "ok",
                "params": {
                    "user_id": user_id,
                    "project": semantic_project,
                    "q": semantic_q,
                    "limit": semantic_limit,
                },
                "result": sem_result,
            }
        except Exception as e:
            semantic_block = {
                "status": "error",
                "error": str(e),
                "params": {
                    "user_id": user_id,
                    "project": semantic_project,
                    "q": semantic_q,
                    "limit": semantic_limit,
                },
                "result": None,
            }

    # =========================
    # v2: summary / sources / meta
    # =========================

    semantic_result = (semantic_block or {}).get("result") or {}
    semantic_summary_text = semantic_result.get("summary") or ""

    # Texto principal del resumen:
    # 1) summary consolidado de Firestore (si existe),
    # 2) si no, usamos el resumen semántico como fallback.
    summary_text = summary_data.get("summary") or semantic_summary_text or ""

    summary_v2 = {
        "user_id": summary_data.get("user_id", user_id),
        "count": summary_data.get("count"),
        "updated_at": summary_data.get("updated_at"),
        "summary": summary_text,
        # Por ahora usamos el resumen semántico (si existe) como highlight único.
        "highlights": [semantic_summary_text] if semantic_summary_text else [],
        # Los próximos pasos podemos dejarlos vacíos y,
        # si hace falta, se calculan en capas superiores.
        "next_steps": [],
    }

    # TODO: cuando integremos Task Engine acá, reemplazar [] por la lista real
    tasks_list: list = []

    sources = {
        # Exponemos semantic_v2 completo, con status + params + result,
        # para no perder información de error ni trazas.
        "semantic_v2": semantic_block,
        "recent": recent_block,
        "tasks": tasks_list,
    }

    meta = {
        "user_id": user_id,
        "project": project or semantic_project,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "engine_version": "context_bundle_v2",
    }

    # Respuesta final: v2 + campos legacy
    return {
        "status": "ok",
        "user_id": user_id,
        "system_rule": system_rule,
        "summary": summary_v2,
        "sources": sources,
        "meta": meta,
        # Legacy (para no romper nada que todavía mire estos campos antiguos)
        "recent": recent_block,
        "semantic_v2": semantic_block,
    }
