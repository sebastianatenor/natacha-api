from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
import os
import requests

from natacha_brain import (
    fetch_context,
    build_prompt,
    SERVICE_URL,
    search_related_memories,
)

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-4o-mini"


# ============================================================
# AUTO MEMORY HELPERS
# ============================================================


def _should_store_message(msg: str) -> bool:
    """
    Define si el mensaje del usuario es relevante como memoria.
    Más adelante se puede expandir con reglas más avanzadas.
    """
    if not msg:
        return False

    # evitar guardar mensajes triviales
    trivial = ["hola", "dale", "ok", "si", "sí", "gracias"]
    if msg.lower().strip() in trivial:
        return False

    # si menciona temas del negocio, lo guardamos
    keywords = ["Sophie", "Jamin", "grúa", "China", "LLVC", "importación", "vial"]
    if any(k.lower() in msg.lower() for k in keywords):
        return True

    return False


def _store_raw_memory(user_id: str, note: str):
    """
    Llama al motor de memoria para guardar automáticamente la conversación.
    - Guarda memoria cruda en /memory/engine/raw
    - Guarda memoria v2 en /memory/v2/store para búsquedas semánticas
    Ignora errores silenciosamente para no romper el flujo.
    """
    try:
        base = SERVICE_URL.rstrip("/")

        # 1) memoria cruda normalizada
        url_raw = f"{base}/memory/engine/raw"
        payload_raw = {
            "user_id": user_id,
            "note": note,
            "kind": "conversation",
            "importance": "normal",
            "source": "natacha-auto",
        }
        requests.post(url_raw, json=payload_raw, timeout=5)

        # 2) memoria v2 para búsquedas semánticas
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
        # nunca romper la conversación por un problema de memoria
        pass


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint principal de Natacha:

    1. Pide contexto al motor de memoria (/memory/engine/context_bundle) vía natacha_brain.fetch_context
    2. Construye el prompt base con memoria + reglas vía natacha_brain.build_prompt
    3. Busca memorias v2 relacionadas al mensaje actual
    4. Agrega el mensaje del usuario
    5. Si hay OPENAI_API_KEY, llama al modelo externo; si no, devuelve el prompt que usaría
    6. TODOS los errores se devuelven en JSON (no hay más 'Internal Server Error' plano)
    """

    try:
        # 1) Traer contexto desde el motor de memoria
        ctx = fetch_context(user_id=payload.user_id)

        # 2) Construir el prompt con memoria consolidada
        base_prompt = build_prompt(ctx)

        # 2b) Guardar memoria de conversación si aplica
        try:
            if _should_store_message(payload.message):
                _store_raw_memory(payload.user_id, payload.message)
        except Exception:
            # Nunca romper la respuesta por un problema de memoria
            pass

        # 3) Buscar memorias semánticamente relacionadas al mensaje actual
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
                        # tolerante a distintos nombres de campo
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
            # si falla la búsqueda semántica, seguimos sin cortar
            related_block = ""

        # 4) Prompt completo que se habría usado
        system_content = (base_prompt + related_block).strip()
        full_prompt = system_content + f"\n\nUser message:\n{payload.message}"

        # 5) Si no hay OPENAI_API_KEY, devolvemos el prompt y un aviso
        if not OPENAI_API_KEY:
            return {
                "answer": (
                    "⚠️ Natacha está conectada al motor de memoria, "
                    "pero falta configurar la variable de entorno OPENAI_API_KEY "
                    "en Cloud Run para poder llamar al modelo.\n\n"
                    "Mientras tanto, este es el prompt que usaría:\n\n"
                    f"{full_prompt}"
                ),
                "used_prompt": full_prompt,
                "model_called": False,
                "error": "missing_openai_api_key",
            }

        # 6) Intentar llamar al modelo externo (OpenAI u otro compatible)
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
            # Error en la llamada al modelo, pero la API sigue viva
            return {
                "answer": (
                    "⚠️ Hubo un problema al llamar al modelo externo. "
                    "Revisá la configuración de la API key o la red."
                ),
                "used_prompt": full_prompt,
                "model_called": True,
                "error": "model_call_failed",
                "detail": str(e),
            }

    except Exception as e:
        # Cualquier error preparando contexto/prompt también vuelve en JSON
        return {
            "answer": (
                "⚠️ Error interno en Natacha al preparar el contexto o el prompt. "
                "Revisá logs de Cloud Run para más detalles."
            ),
            "used_prompt": None,
            "model_called": False,
            "error": "internal_natacha_error",
            "detail": str(e),
        }
