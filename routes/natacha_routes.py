from typing import Optional
import os
import requests

from fastapi import APIRouter
from pydantic import BaseModel

from natacha_brain import (
    fetch_context,
    build_prompt,
)

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ============================================================
# MODELOS
# ============================================================

class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-4o-mini"


# ============================================================
# ENDPOINT PRINCIPAL
# ============================================================

@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint principal de Natacha.

    - Intenta usar contexto/memoria
    - Si falla, degrada de forma segura
    - Nunca bloquea la respuesta del modelo
    """

    # --------------------------------------------------------
    # 1) Construcción de prompt (TOLERANTE A FALLOS)
    # --------------------------------------------------------
    try:
        ctx = fetch_context(user_id=payload.user_id)
        system_content = build_prompt(ctx).strip()
    except Exception as e:
        # ⚠️ Contexto roto → seguimos igual
        system_content = (
            "You are Natacha, an executive cognitive assistant. "
            "Context and memory are temporarily unavailable, "
            "but you must still respond clearly and helpfully.\n\n"
            f"[Context error: {str(e)}]"
        )

    # --------------------------------------------------------
    # 2) Verificación API KEY
    # --------------------------------------------------------
    if not OPENAI_API_KEY:
        return {
            "answer": (
                "⚠️ Natacha está operativa, pero falta configurar "
                "OPENAI_API_KEY en Cloud Run."
            ),
            "model_called": False,
            "error": "missing_openai_api_key",
        }

    # --------------------------------------------------------
    # 3) Llamada directa a OpenAI (con debug real)
    # --------------------------------------------------------
    try:
        url = "https://api.openai.com/v1/chat/completions"

        req_payload = {
            "model": payload.model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": payload.message},
            ],
        }

        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=req_payload,
            timeout=30,
        )

        # ---- errores HTTP explícitos ----
        if resp.status_code >= 400:
            body = (resp.text or "")[:2000]
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{resp.status_code}",
                "detail": body,
            }

        data = resp.json()
        answer = data["choices"][0]["message"]["content"]

        return {
            "answer": answer,
            "model_called": True,
            "error": None,
        }

    except Exception as e:
        return {
            "answer": "⚠️ Error al llamar al modelo externo (exception).",
            "model_called": False,
            "error": "openai_exception",
            "detail": str(e),
        }
