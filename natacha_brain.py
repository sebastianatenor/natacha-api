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

    return base.strip()
