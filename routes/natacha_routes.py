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
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"


# ============================================================
# MODELOS
# ============================================================

class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-5.2"


# ============================================================
# ENDPOINT PRINCIPAL
# ============================================================

@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint cognitivo principal de Natacha.
    Usa OpenAI Responses API (GPT-5.2).
    """

    # --------------------------------------------------------
    # 1) Construir prompt (tolerante a fallos de memoria)
    # --------------------------------------------------------
    try:
        ctx = fetch_context(user_id=payload.user_id)
        base_prompt = build_prompt(ctx).strip()
    except Exception:
        base_prompt = (
            "You are Natacha, an executive cognitive assistant. "
            "The memory system is temporarily unavailable. "
            "Respond clearly, safely, and helpfully."
        )

    full_prompt = (
        f"{base_prompt}\n\n"
        f"User message:\n{payload.message}"
    )

    if not OPENAI_API_KEY:
        return {
            "answer": "⚠️ Falta configurar OPENAI_API_KEY en Cloud Run.",
            "model_called": False,
            "error": "missing_openai_api_key",
        }

    # --------------------------------------------------------
    # 2) Llamada CORRECTA a OpenAI Responses API
    # --------------------------------------------------------
    try:
        resp = requests.post(
            OPENAI_RESPONSES_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": payload.model or "gpt-5.2",
                "input": full_prompt,
            },
            timeout=30,
        )

        if resp.status_code >= 400:
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{resp.status_code}",
                "detail": resp.text[:2000],
            }

        data = resp.json()

        # ----------------------------------------------------
        # 3) Extraer texto de salida
        # ----------------------------------------------------
        answer_text = ""

        for item in data.get("output", []):
            if item.get("type") == "message":
                for block in item.get("content", []):
                    if block.get("type") == "output_text":
                        answer_text += block.get("text", "")

        answer_text = answer_text.strip()

        if not answer_text:
            answer_text = "⚠️ El modelo respondió sin texto utilizable."

        return {
            "answer": answer_text,
            "model_called": True,
            "error": None,
        }

    except Exception as e:
        return {
            "answer": "⚠️ Error inesperado llamando al modelo.",
            "model_called": False,
            "error": "openai_exception",
            "detail": str(e),
        }
