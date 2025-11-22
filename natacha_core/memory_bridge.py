import os
from typing import List, Optional, Dict, Any

import requests

# === Configuración de endpoints ===
# Legacy (motor viejo de memorias)
MEMORY_API_URL = os.getenv("MEMORY_API_URL", "http://127.0.0.1:8000/memory/v2").rstrip("/")

# Core HTTP base (Cloud Run / local)
NATACHA_API_BASE = os.getenv("NATACHA_API_BASE", "").rstrip("/")


def _resolve_core_base() -> str:
    """
    Devuelve la base HTTP para hablar con el núcleo de Natacha.
    Prioriza NATACHA_API_BASE y, si no está, deriva de MEMORY_API_URL.
    """
    if NATACHA_API_BASE:
        return NATACHA_API_BASE

    base = MEMORY_API_URL
    if base.endswith("/memory/v2"):
        base = base[: -len("/memory/v2")]
    return base


# ============================================================
#  A) LEGACY: store_memory y retrieve_context básico
# ============================================================

def store_memory(user: str, text: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Guarda una nueva memoria contextual asociada al usuario en el backend legacy.
    (Usa /memory/v2/store si está disponible).
    """
    payload = {
        "items": [
            {
                "text": text,
                "tags": tags or ["core-context"],
            }
        ]
    }
    try:
        r = requests.post(f"{MEMORY_API_URL}/store", json=payload, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "source": "legacy-store"}


def retrieve_context(
    limit: int = 5,
    user: Optional[str] = None,
    semantic_project: Optional[str] = None,
    semantic_q: Optional[str] = None,
    semantic_limit: int = 5,
    recent_limit: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Motor unificado de contexto:

    - Si NO se pasa user/semantic_* -> usa backend legacy (/memory/v2/ops/memory-info).
    - Si se pasa user o semantic_* -> usa /memory/engine/context_bundle
      que ya incluye semantic_v2 cuando se le pasan parámetros semánticos.
    """
    # --- Rama legacy (como antes) ---
    if not user and not semantic_project and not semantic_q:
        try:
            r = requests.get(f"{MEMORY_API_URL}/ops/memory-info", timeout=5)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                return {"status": "empty", "context": [], "source": "legacy"}
            data.setdefault("source", "legacy")
            return data
        except Exception as e:
            return {"status": "unreachable", "error": str(e), "source": "legacy"}

    # --- Rama avanzada: context_bundle + semantic_v2 ---
    base = _resolve_core_base()
    params: Dict[str, Any] = {
        "user_id": user,
        "recent_limit": recent_limit or limit,
    }
    if semantic_project:
        params["semantic_project"] = semantic_project
    if semantic_q:
        params["semantic_q"] = semantic_q
    params["semantic_limit"] = semantic_limit

    try:
        r = requests.get(f"{base}/memory/engine/context_bundle", params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Metadatos útiles para debug (esto es lo que viste en el demo)
        data.setdefault("source", "context_bundle")
        data.setdefault("params_used", params)
        return data
    except Exception as e:
        return {"status": "error", "error": str(e), "source": "context_bundle", "params_used": params}


# ============================================================
#  B) NUEVO: escritura directa en semantic_memory_v2
# ============================================================

def store_semantic_memory_event(
    user_id: str,
    project: str,
    text: str,
    tags: Optional[List[str]] = None,
    people: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Guarda un evento en semantic_memory_v2 vía HTTP:
    POST /memory/v2/semantic/add

    Esto es el "hook" para que cualquier módulo pueda alimentar la memoria semántica
    sin hablar directo con Firestore ni con OpenAI.
    """
    base = _resolve_core_base()
    payload = {
        "user_id": user_id,
        "project": project,
        "text": text,
        "tags": tags or [],
        "people": people or [],
    }
    try:
        r = requests.post(f"{base}/memory/v2/semantic/add", json=payload, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "source": "semantic_v2-add"}


# ============================================================
#  C) NUEVO: construcción de bloque de contexto compuesto
# ============================================================

def build_context_block(
    user: str,
    project: Optional[str] = None,
    query: Optional[str] = None,
    semantic_limit: int = 5,
    recent_limit: int = 20,
) -> Dict[str, Any]:
    """
    Devuelve un bloque de contexto "listo para usar" en prompts del agente,
    combinando:

    - system_rule (core-v1)
    - summary v1 consolidado (texto)
    - summary semántico v2 focalizado (texto)
    - items semánticos más relevantes (lista)
    """
    ctx = retrieve_context(
        limit=recent_limit,
        user=user,
        semantic_project=project,
        semantic_q=query,
        semantic_limit=semantic_limit,
    )

    system_rule = ctx.get("system_rule") or {}
    summary_doc = ctx.get("summary") or {}
    legacy_summary_text: Optional[str] = None
    if isinstance(summary_doc, dict):
        legacy_summary_text = summary_doc.get("summary")

    semantic_block = (ctx.get("semantic_v2") or {}).get("result") or {}
    semantic_summary: Optional[str] = semantic_block.get("summary")
    semantic_items: List[Dict[str, Any]] = semantic_block.get("items") or []

    context_parts: List[str] = []

    # a) Nota de sistema si existe
    note = None
    if isinstance(system_rule, dict):
        note = system_rule.get("note")
    if note:
        context_parts.append(f"SYSTEM RULE (core-v1):\n{note}")

    # b) Summary v1 clásico
    if legacy_summary_text:
        context_parts.append(f"Resumen ejecutivo v1:\n{legacy_summary_text}")

    # c) Summary semántico focalizado
    if semantic_summary:
        context_parts.append(f"Memoria semántica focalizada:\n{semantic_summary}")

    full_context_block = (
        "\n\n---\n\n".join(context_parts) if context_parts else "(sin contexto compuesto)"
    )

    return {
        "raw": ctx,
        "system_rule": system_rule,
        "summary_v1": legacy_summary_text,
        "semantic_summary": semantic_summary,
        "semantic_items": semantic_items,
        "context_block": full_context_block,
    }


def build_chat_messages(
    user: str,
    project: Optional[str],
    query: Optional[str],
    user_message: str,
    semantic_limit: int = 5,
    recent_limit: int = 20,
) -> List[Dict[str, str]]:
    """
    Devuelve una lista de mensajes estilo OpenAI/Gemini:

    [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."},
    ]

    Usando:
    - system_rule (si está) o un texto por defecto
    - el bloque de contexto compuesto (summary v1 + semántica v2)
    - la pregunta actual de Sebastián
    """
    block = build_context_block(
        user=user,
        project=project,
        query=query,
        semantic_limit=semantic_limit,
        recent_limit=recent_limit,
    )

    system_rule = block.get("system_rule")
    system_text: Optional[str] = None
    if isinstance(system_rule, dict):
        system_text = system_rule.get("rule") or system_rule.get("note")

    if not system_text:
        system_text = (
            "Eres Natacha, asistente personal de Sebastián. "
            "Usa el contexto que te paso para razonar antes de responder, "
            "priorizando importaciones de maquinaria, LLVC Global y tareas pendientes."
        )

    context_text = block.get("context_block") or "(sin contexto compuesto)"

    messages: List[Dict[str, str]] = [
        {
            "role": "system",
            "content": system_text,
        },
        {
            "role": "user",
            "content": (
                "Contexto de trabajo consolidado:\n"
                f"{context_text}\n\n"
                "Consulta actual de Sebastián:\n"
                f"{user_message}"
            ),
        },
    ]
    return messages
