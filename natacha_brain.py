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

    system = ctx.get("system_rule", "") or ""
    summary = ctx.get("summary", "") or ""
    error = ctx.get("error", None)

    base = (
        "You are Natacha, an executive AI assistant. "
        "You speak Spanish with an empowered tone.\n\n"
    )

    if error:
        base += f"(⚠️ CONTEXT WARNING: {error})\n\n"

    if system:
        base += f"System rule:\n{system}\n\n"

    if summary:
        base += f"User memory summary:\n{summary}\n\n"

    return base.strip()
