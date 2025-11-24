from typing import Optional, Dict, Any, List
from datetime import datetime  # para meta.generated_at

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

from natacha_core import semantic_memory_v2
from semantic_engine.engine_v2 import build_context_bundle


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
    project: Optional[str] = None,  # para meta.project y futuras fuentes
    recent_limit: int = Query(20, ge=1, le=200),
    include_global_fallback: bool = True,
    # Parámetros opcionales para memoria semántica v2
    semantic_project: Optional[str] = None,
    semantic_q: Optional[str] = None,
    semantic_limit: int = Query(5, ge=1, le=50),
):
    """
    Devuelve un paquete de contexto listo para Natacha (versión legacy v2).

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

    # Derivar próximos pasos (next_steps)
    next_steps: List[str] = []

    # 1) Intentar extraer una línea con "Próximo paso" del resumen semántico
    if semantic_summary_text:
        for line in semantic_summary_text.splitlines():
            lower = line.lower().strip()
            if "próximo paso" in lower or "proximo paso" in lower:
                cleaned = line
                if ")" in cleaned[:5]:
                    cleaned = cleaned.split(")", 1)[1]
                cleaned = cleaned.replace("**", "").strip(" :–-")
                if cleaned:
                    next_steps.append(cleaned)
                break

    # 2) Fallback: si no encontramos nada, usamos la primera línea del summary_text
    if not next_steps and summary_text:
        first_line = summary_text.splitlines()[0].strip()
        if first_line:
            next_steps.append(first_line)

    summary_v2 = {
        "user_id": summary_data.get("user_id", user_id),
        "count": summary_data.get("count"),
        "updated_at": summary_data.get("updated_at"),
        "summary": summary_text,
        "highlights": [semantic_summary_text] if semantic_summary_text else [],
        "next_steps": next_steps,
    }

    tasks_list: list = []  # legacy, todavía no integrado en este endpoint

    sources = {
        "semantic_v2": semantic_block,
        "recent": recent_block,
        "tasks": tasks_list,
    }

    meta = {
        "user_id": user_id,
        "project": project or semantic_project,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "engine_version": "context_bundle_v2_legacy",
    }

    return {
        "status": "ok",
        "user_id": user_id,
        "system_rule": system_rule,
        "summary": summary_v2,
        "sources": sources,
        "meta": meta,
        "recent": recent_block,
        "semantic_v2": semantic_block,
    }


@router.get("/context_bundle_v2")
def memory_context_bundle_v2(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    """
    NUEVO endpoint: usa semantic_engine.engine_v2.build_context_bundle

    - Lee memorias recientes desde memory_engine.list_recent_memories
    - Lee tareas reales desde la colección assistant_tasks (Firestore)
    - (Por ahora) eventos = []
    - Devuelve:
        {
          "summary": {...},
          "tasks": {"pending": [...], "done": [...]},
          "events": [...],
          "memories": [...]
        }
    """
    # 1) memorias recientes
    memories = list_recent_memories(user_id=user_id, limit=limit)

    # 2) tareas desde assistant_tasks
    tasks_col = db.collection("assistant_tasks")
    # limitamos a 200 para no traer todo el universo
    docs = tasks_col.limit(200).stream()
    tasks: List[Dict[str, Any]] = []
    for d in docs:
        data = d.to_dict()
        data["id"] = d.id
        if project and (data.get("project") or "") != project:
            continue
        tasks.append(data)

    # 3) eventos (por ahora vacío, luego calendar engine)
    events: List[Dict[str, Any]] = []

    bundle = build_context_bundle(
        user_id=user_id,
        project=project,
        memories=memories,
        tasks=tasks,
        events=events,
        limit=limit,
    )
    return bundle

# --- Back-compat alias ---
v1_router = router


# ============================
# v2 puro: /memory/engine/context_bundle_v2
# ============================
@router.get("/context_bundle_v2")
def memory_context_bundle_v2(
    user_id: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = Query(20, ge=1, le=200),
):
    """
    Versión v2 pura basada en semantic_engine.engine_v2.build_context_bundle.

    Devuelve directamente:
    - summary
    - tasks
    - events
    - raw
    """
    # 1) memorias recientes (usa el motor ya existente)
    recent_memories = list_recent_memories(user_id=user_id, limit=limit)

    # 2) tareas desde assistant_tasks (Firestore)
    tasks: List[Dict[str, Any]] = []
    try:
        col = db.collection("assistant_tasks")
        q = col
        if project:
            q = q.where("project", "==", project)
        for d in q.stream():
            data = d.to_dict()
            data["id"] = d.id
            tasks.append(data)
    except Exception:
        # Si Firestore falla, no rompemos el contexto
        tasks = []

    # 3) eventos: por ahora dejamos hook vacío (Calendar Engine v1.5)
    #    Más adelante enchufamos aquí Google Calendar / proxy.
    events: List[Dict[str, Any]] = []

    bundle = build_context_bundle(
        user_id=user_id or "anonymous",
        project=project,
        memories=recent_memories,
        tasks=tasks,
        events=events,
        limit=limit,
    )
    return bundle
