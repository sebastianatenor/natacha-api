import os
from typing import Any, Dict, List, Optional

import requests

SERVICE_URL = os.getenv(
    "SERVICE_URL",
    "https://natacha-api-422255208682.us-central1.run.app",
)


def fetch_context(user_id: str, recent_limit: int = 20) -> Dict[str, Any]:
    """
    Consulta el bundle de memoria consolidada desde Cloud Run
    y garantiza devolver SIEMPRE un diccionario.
    """
    try:
        url = f"{SERVICE_URL}/memory/engine/context_bundle"
        params = {
            "user_id": user_id,
            "recent_limit": recent_limit,
            "include_global_fallback": True,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, dict):
            return {
                "summary": {},
                "recent": [],
                "system_rule": {},
                "user_id": user_id,
            }

        return {
            "summary": data.get("summary") or {},
            "recent": data.get("recent") or [],
            "system_rule": data.get("system_rule") or {},
            "user_id": user_id,
        }

    except Exception as e:
        # Devuelve dict seguro en caso de error
        return {
            "summary": {},
            "recent": [],
            "system_rule": {},
            "error": f"context_fetch_error: {e}",
            "user_id": user_id,
        }


# ============================================================
# BÚSQUEDA SEMÁNTICA v2
# ============================================================

def semantic_search(
    user_id: str,
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Usa /memory/v2/search para encontrar memorias relevantes por significado.
    Filtra por tag user:{user_id}.
    """
    query = (query or "").strip()
    if not query:
        return []

    payload = {
        "query": query,
        "top_k": top_k,
        "tags": [f"user:{user_id}"],
        "use_semantic": True,
    }

    try:
        url = f"{SERVICE_URL}/memory/v2/search"
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not isinstance(data, dict):
            return []

        items = data.get("items") or []
        if not isinstance(items, list):
            return []

        return items

    except Exception:
        # Nunca romper el flujo por un problema de búsqueda semántica
        return []


def _format_semantic_block(items: List[Dict[str, Any]], max_items: int = 5) -> str:
    """
    Convierte los resultados semánticos en texto breve para el prompt.
    """
    if not items:
        return ""

    lines: List[str] = []
    for i, item in enumerate(items[:max_items], start=1):
        text = str(item.get("text", "")).strip()
        tags = item.get("tags") or []
        if len(text) > 220:
            text = text[:220].rstrip() + "…"

        if tags:
            lines.append(f"- {text} (tags: {', '.join(tags)})")
        else:
            lines.append(f"- {text}")

    if not lines:
        return ""

    return "Semantic memories:\n" + "\n".join(lines)


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(
    ctx: Dict[str, Any],
    semantic_items: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Construye el prompt base con sistema + memoria consolidada + reglas
    + (opcional) memorias semánticas v2.
    """

    system_raw = ctx.get("system_rule") or {}
    summary_raw = ctx.get("summary") or {}
    error = ctx.get("error", None)

    # Normalización:
    # - system_rule suele venir como dict {"rule": "...", "version": "...", ...}
    # - summary suele venir como dict {"summary": "...", "count": N, ...}
    if isinstance(system_raw, dict):
        system_text = system_raw.get("rule", "") or ""
    else:
        system_text = str(system_raw) if system_raw else ""

    if isinstance(summary_raw, dict):
        summary_text = summary_raw.get("summary", "") or ""
    else:
        summary_text = str(summary_raw) if summary_raw else ""

    base = (
        "You are Natacha, an executive AI assistant. "
        "You speak Spanish with an empowered tone.\n\n"
    )

    if error:
        base += f"(⚠️ CONTEXT WARNING: {error})\n\n"

    if system_text.strip():
        base += f"System rule:\n{system_text.strip()}\n\n"

    if summary_text.strip():
        base += f"User memory summary:\n{summary_text.strip()}\n\n"

    # Bloque extra: memorias semánticas v2
    if semantic_items:
        semantic_block = _format_semantic_block(semantic_items)
        if semantic_block:
            base += semantic_block + "\n\n"

    return base.strip()
