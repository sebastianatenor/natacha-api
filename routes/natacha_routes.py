# routes/natacha_routes.py

import os
import time
from typing import Dict, Any, List

from fastapi import APIRouter, HTTPException, Body

from unified_core.memory_lazy import get_memory_index
from ops.system.manifest_decider import ManifestDecider
from ops.openai_client import chat_completion

# Router
router = APIRouter(prefix="/natacha", tags=["natacha"])

MODEL = os.getenv("NATACHA_MODEL", "gpt-5.2-chat-latest")
decider = ManifestDecider()


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def _safe_memory_state() -> Dict[str, Any]:
    try:
        idx = get_memory_index()
        count = getattr(idx, "items_count", None)
        if count is None:
            try:
                count = len(getattr(idx, "store", []))
            except Exception:
                count = None

        return {
            "loaded": True,
            "items_count": count
        }
    except Exception as e:
        return {
            "loaded": False,
            "error": str(e)
        }


def _load_active_manifests_from_fs() -> List[str]:
    """
    Carga pasiva de manifiestos desde /docs/manifests.
    No depende de loaders inexistentes.
    """
    base_path = "/app/docs/manifests"
    try:
        return sorted([
            f for f in os.listdir(base_path)
            if f.endswith(".md") and not f.startswith("_")
        ])
    except Exception:
        return []


def _build_system_context() -> Dict[str, Any]:
    """
    Contexto cognitivo PASIVO.
    No ejecuta acciones.
    """
    manifests = _load_active_manifests_from_fs()

    system_state = {
        "memory": _safe_memory_state(),
        "manifests": {
            "active_count": len(manifests),
            "active": manifests
        }
    }

    suggestions = decider.evaluate(
        system_state=system_state,
        recent_context=[],
        active_project=None
    )

    return {
        "system_state": system_state,
        "suggestions": [
            {
                "level": getattr(s, "level", "info"),
                "title": getattr(s, "title", ""),
                "message": getattr(s, "message", ""),
                "source_manifest": getattr(s, "source_manifest", "unknown"),
            }
            for s in suggestions
        ]
    }


def _render_system_prompt(context: Dict[str, Any]) -> str:
    lines: List[str] = []

    lines.append("You are Natacha, an executive-grade AI assistant.")
    lines.append("You MUST respect the active cognitive manifests.")
    lines.append("You MUST NOT execute actions unless explicitly requested.")
    lines.append("")

    lines.append("=== SYSTEM STATE ===")
    lines.append(str(context["system_state"]))
    lines.append("")

    lines.append("=== MANIFEST GUIDANCE ===")
    for s in context["suggestions"]:
        lines.append(
            f"- [{s['level'].upper()}] {s['title']}: {s['message']} "
            f"(source: {s['source_manifest']})"
        )

    return "\n".join(lines)


# ---------------------------------------------------------
# Main endpoint
# ---------------------------------------------------------

@router.post("/chat")
def natacha_chat(payload: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """
    Chat principal del agente Natacha.
    Consciente de manifiestos y estado cognitivo.
    """

    user_input = payload.get("message")
    if not user_input:
        raise HTTPException(status_code=400, detail="Missing 'message'")

    timestamp = time.time()

    # 1. Contexto cognitivo
    cognitive_context = _build_system_context()
    system_prompt = _render_system_prompt(cognitive_context)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]

    try:
        response = chat_completion(
            model=MODEL,
            messages=messages
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LLM failure: {str(e)}"
        )

    return {
        "timestamp": timestamp,
        "model": MODEL,
        "response": response,
        "cognitive_state": cognitive_context
    }
