import os
import requests

SERVICE_URL = os.getenv("SERVICE_URL", "https://natacha-api-422255208682.us-central1.run.app")


def fetch_context(user_id: str):
    """
    Consulta el bundle de memoria consolidada desde Cloud Run
    y garantiza devolver SIEMPRE un diccionario.
    """

    try:
        url = f"{SERVICE_URL}/memory/engine/context_bundle?user_id={user_id}&recent_limit=20"
        resp = requests.get(url, timeout=10)

        resp.raise_for_status()

        data = resp.json()

        # 🔒 GARANTÍA: siempre dict
        if not isinstance(data, dict):
            return {"summary": "", "recent": [], "system_rule": ""}

        # Normalización mínima
        return {
            "summary": data.get("summary", ""),
            "recent": data.get("recent", []),
            "system_rule": data.get("system_rule", ""),
            "user_id": user_id,
        }

    except Exception as e:
        # Devuelve dict seguro en caso de error
        return {
            "summary": "",
            "recent": [],
            "system_rule": "",
            "error": f"context_fetch_error: {e}",
            "user_id": user_id,
        }


def build_prompt(ctx: dict) -> str:
    """
    Construye el prompt base con sistema + memoria consolidada + reglas.
    DEBE recibir siempre un dict desde fetch_context().
    """

    system_raw = ctx.get("system_rule") or {}
    summary_raw = ctx.get("summary") or {}
    recent_raw = ctx.get("recent") or []
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
        "You are Natacha, an executive AI assistant for Sebastián Atenor (LLVC Global). "
        "You speak Spanish (vos) with an empowered but clear and concrete tone.\n\n"
    )

    if error:
        base += f"(⚠️ CONTEXT WARNING: {error})\n\n"

    if system_text.strip():
        base += f"System rule:\n{system_text.strip()}\n\n"

    if summary_text.strip():
        base += f"User memory summary:\n{summary_text.strip()}\n\n"

    # Opcional: incluir últimos recuerdos crudos como bullets
    if isinstance(recent_raw, list) and recent_raw:
        notes = []
        for item in recent_raw[:5]:
            note = ""
            if isinstance(item, dict):
                note = item.get("note") or item.get("text") or ""
            else:
                note = str(item)
            note = (note or "").strip()
            if note:
                notes.append(f"- {note}")
        if notes:
            base += "Recent raw memories:\n" + "\n".join(notes) + "\n\n"

    return base.strip()


def search_related_memories(user_id: str, query: str, top_k: int = 5):
    """
    Busca memorias v2 relacionadas semánticamente al mensaje actual.

    Usa /memory/v2/search con:
    - query: mensaje actual
    - top_k: cantidad de resultados
    - tags: ["user:<user_id>"] para acotar por usuario
    """
    try:
        url = f"{SERVICE_URL.rstrip('/')}/memory/v2/search"
        payload = {
            "query": query,
            "top_k": top_k,
            "tags": [f"user:{user_id}"],
            "use_semantic": True,
        }
        resp = requests.post(url, json=payload, timeout=8)
        resp.raise_for_status()
        data = resp.json()

        # Tolerante al shape de la respuesta
        if isinstance(data, dict):
            if "items" in data and isinstance(data["items"], list):
                return data["items"]
            if "results" in data and isinstance(data["results"], list):
                return data["results"]

        return []
    except Exception:
        # Nunca romper el flujo por un problema de búsqueda
        return []
