import requests
import os

SERVICE_URL = os.getenv("SERVICE_URL", "https://natacha-api-422255208682.us-central1.run.app")


def fetch_context(user_id: str, project: str = None):
    """
    Llama al motor /memory/engine/context_bundle y devuelve el paquete completo.
    """
    params = {"user_id": user_id, "recent_limit": 20}
    if project:
        params["project"] = project
        params["semantic_project"] = project
        params["semantic_q"] = f"estado {project}"
        params["semantic_limit"] = 5

    try:
        r = requests.get(f"{SERVICE_URL}/memory/engine/context_bundle", params=params, timeout=10)
        return r.json()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "system_rule": None,
            "summary": None,
            "recent": {},
            "semantic_v2": {},
        }


def build_prompt(context: dict, message: str) -> str:
    """
    Construye el prompt que se le pasa al modelo.
    Ahora incluye semantic_v2.summary integrado.
    """

    parts = []

    # 1. Rol
    parts.append(
        "You are Natacha, an executive AI assistant for Sebastián Atenor (LLVC Global). "
        "You speak Spanish (vos) with an empowered but clear and concrete tone."
    )

    # 2. System Rule
    system_rule = context.get("system_rule")
    if system_rule and system_rule.get("rule"):
        parts.append(f"\nSystem rule:\n{system_rule['rule']}")

    # 3. User memory summary (resumen ejecutivo)
    summary = context.get("summary")
    if summary and summary.get("summary"):
        parts.append(f"\nUser memory summary:\n{summary['summary']}")

    # 4. Semantic v2 – integración explícita
    semantic_block = context.get("semantic_v2") or {}
    semantic_result = semantic_block.get("result") or {}
    semantic_summary = semantic_result.get("summary")

    if semantic_summary:
        parts.append("\nMemoria semántica del proyecto (v2):\n" + semantic_summary)

    # 5. Recent messages (solo para dar color contextual)
    recent = context.get("recent", {})
    items = recent.get("items", [])
    if items:
        recent_texts = []
        for it in items[:5]:
            note = it.get("note")
            if note:
                recent_texts.append(f"- {note}")
        if recent_texts:
            parts.append("\nMensajes recientes relevantes:\n" + "\n".join(recent_texts))

    # 6. Mensaje actual del usuario
    parts.append("\nMensaje del usuario:\n" + message)

    return "\n\n".join(parts)


def call_llm(prompt: str) -> str:
    """
    Llama al modelo de OpenAI usando la API definida en SERVICE_URL (tu backend).
    """
    try:
        r = requests.post(
            f"{SERVICE_URL}/ops/core/analyze",
            json={"prompt": prompt},
            timeout=20,
        )
        data = r.json()
        return data.get("answer") or data.get("text") or "Sin respuesta del modelo."
    except Exception as e:
        return f"[Error llamando al modelo] {e}"


def handle_message(user_id: str, project: str, message: str):
    """
    Lógica principal: obtiene contexto, arma prompt, y llama al modelo.
    """

    ctx = fetch_context(user_id=user_id, project=project)
    prompt = build_prompt(ctx, message)
    answer = call_llm(prompt)

    return {
        "answer": answer,
        "used_prompt": prompt,
        "model_called": True,
    }

# --------------------------------------------------------------------
# Compat: helper legado para búsquedas de memoria relacionadas
# --------------------------------------------------------------------

def search_related_memories(user_id, project, message, limit=5):
    """
    Helper legado usado por algunos endpoints (ej. /natacha/respond).
    Hoy delega en /memory/engine/context_bundle con parámetros semánticos.

    No escribe nada, solo lee contexto.
    """
    import os
    import requests

    base = (
        os.getenv("SERVICE_URL")
        or os.getenv("NATACHA_SERVICE_URL")
        or "http://localhost:8080"
    )

    params = {
        "user_id": user_id,
        "recent_limit": 20,
        "semantic_limit": limit,
    }

    if project:
        params["project"] = project
        params["semantic_project"] = project

    # usamos el propio mensaje como query semántica
    params["semantic_q"] = message

    try:
        r = requests.get(
            f"{base}/memory/engine/context_bundle",
            params=params,
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "params_used": params,
            "result": None,
        }

    return {
        "status": "ok",
        "params_used": params,
        "result": data.get("semantic_v2"),
    }
