from datetime import datetime

def build_context_bundle(
    user_id: str = None,
    recent_limit: int = 20,
    include_global_fallback: bool = True
):
    """
    Versión mínima estable para que el motor unificado funcione.
    Luego la reemplazamos por la versión completa.
    """

    return {
        "user_id": user_id or "anonymous",
        "generated_at": datetime.utcnow().isoformat(),
        "recent_limit": recent_limit,
        "global_fallback": include_global_fallback,
        "context_blocks": [
            {"type": "system", "content": "Unified context engine v2 placeholder."}
        ]
    }
