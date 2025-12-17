from typing import Optional
import os
import requests

from fastapi import APIRouter
from pydantic import BaseModel

from natacha_brain import (
    fetch_context,
    build_prompt,
    SERVICE_URL,
    search_related_memories,
)

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ============================================================
# MODELOS DE ENTRADA
# ============================================================

class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-4o-mini"


# ============================================================
# AUTO MEMORY HELPERS (UNIFICADOS)
# ============================================================

def _should_store_message(msg: str) -> bool:
    """
    Define si el mensaje del usuario es relevante como memoria.
    Regla conservadora: evita ruido.
    """
    if not msg:
        return False

    trivial = ["hola", "dale", "ok", "si", "sí", "gracias"]
    if msg.lower().strip() in trivial:
        return False

    keywords = [
        "sophie",
        "jamin",
        "grúa",
        "china",
        "llvc",
        "importación",
        "vial",
        "proveedor",
        "cliente",
    ]

    return any(k in msg.lower() for k in keywords)


def _store_raw_memory(user_id: str, note: str):
    """
    Guarda memoria de conversación de forma segura.
    - Memoria cruda
    - Memoria v2 semántica
    Nunca rompe el flujo conversacional.
    """
    try:
        base = SERVICE_URL.rstrip("/")

        # 1) Memoria cruda
        url_raw = f"{base}/memory/engine/raw"
        payload_raw = {
            "user_id": user_id,
            "note": note,
            "kind": "conversation",
            "importance": "normal",
            "source": "natacha-auto",
        }
        requests.post(url_raw, json=payload_raw, timeout=5)

        # 2) Memoria v2 (semántica)
        url_v2 = f"{base}/memory/v2/store"
        payload_v2 = {
            "items": [
                {
                    "text": note,
                    "tags": ["conversation", "natacha-auto", f"user:{user_id}"],
                    "meta": {
                        "user_id": user_id,
                        "kind": "conversation",
                        "source": "natacha-auto",
                    },
                }
            ]
        }
        requests.post(url_v2, json=payload_v2, timeout=5)

    except Exception:
        pass  # nunca romper la conversación


# ============================================================
# EXECUTIVE / COGNITIVE OBSERVABILITY (PASIVO)
# ============================================================

def _get_executive_observations() -> str:
    """
    Obtiene observaciones ejecutivas PASIVAS del sistema.
    - No ejecuta acciones
    - No modifica estado
    - Si falla, se ignora
    """
    try:
        url = f"{SERVICE_URL}/ops/system/decide"
        resp = requests.get(url, timeout=3)
        data = resp.json()

        suggestions = (
            data.get("suggestions")
            or data.get("recommendations")
            or []
        )

        if not suggestions:
            return ""

        lines = []
        for s in suggestions:
            title = s.get("action") or s.get("title") or "Observation"
            reason = s.get("reason") or s.get("message") or ""
            lines.append(f"- {title}: {reason}")

        return (
            "\n\n[Executive Observations]\n"
            + "\n".join(lines)
            + "\n\nAsk the user if they want to act on any of these."
        )

    except Exception:
        return ""


# ============================================================
# ENDPOINT PRINCIPAL
# ============================================================

@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint principal de Natacha.

    Flujo:
    1. Trae contexto desde memoria
    2. Construye prompt base
    3. Guarda memoria (si aplica)
    4. Busca memorias semánticas relacionadas
    5. Inyecta observaciones ejecutivas (PASIVO)
    6. Llama al modelo (si hay API key)
    """

    try:
        # 1) Contexto desde memoria
        ctx = fetch_context(user_id=payload.user_id)

        # 2) Prompt base
        base_prompt = build_prompt(ctx)

        # 3) Guardar memoria si aplica
        try:
            if _should_store_message(payload.message):
                _store_raw_memory(payload.user_id, payload.message)
        except Exception:
            pass

        # 4) Memoria semántica relacionada
        related_block = ""
        try:
            related = search_related_memories(
                user_id=payload.user_id,
                query=payload.message,
                top_k=5,
            )
            if related:
                bullets = []
                for item in related:
                    text = ""
                    if isinstance(item, dict):
                        text = (
                            item.get("text")
                            or item.get("summary")
                            or item.get("note")
                            or ""
                        )
                    else:
                        text = str(item)

                    text = (text or "").strip()
                    if text:
                        bullets.append(f"- {text}")

                if bullets:
                    related_block = (
                        "\n\nMemoria relevante para este mensaje (v2):\n"
                        + "\n".join(bullets)
                    )
        except Exception:
            related_block = ""

        # 5) Observaciones ejecutivas (PASIVO)
        executive_block = _get_executive_observations()

        # Prompt final
        system_content = (
            base_prompt + executive_block + related_block
        ).strip()

        full_prompt = system_content + f"\n\nUser message:\n{payload.message}"

        # 6) Sin API key → modo diagnóstico
        if not OPENAI_API_KEY:
            return {
                "answer": (
                    "⚠️ Natacha está conectada al motor cognitivo, "
                    "pero falta configurar OPENAI_API_KEY.\n\n"
                    "Este es el prompt que usaría:\n\n"
                    f"{full_prompt}"
                ),
                "used_prompt": full_prompt,
                "model_called": False,
                "error": "missing_openai_api_key",
            }

        # 7) Llamada al modelo
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": payload.model or "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": payload.message},
                    ],
                },
                timeout=30,
            )

            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]

            return {
                "answer": answer,
                "used_prompt": system_content,
                "model_called": True,
            }

        except Exception as e:
            return {
                "answer": (
                    "⚠️ Hubo un problema al llamar al modelo externo. "
                    "Revisá la API key o la red."
                ),
                "used_prompt": full_prompt,
                "model_called": True,
                "error": "model_call_failed",
                "detail": str(e),
            }

    except Exception as e:
        return {
            "answer": (
                "⚠️ Error interno preparando contexto o prompt. "
                "Revisá logs de Cloud Run."
            ),
            "used_prompt": None,
            "model_called": False,
            "error": "internal_natacha_error",
            "detail": str(e),
        }
