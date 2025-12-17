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
OPENAI_BASE_URL = "https://api.openai.com/v1/responses"


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
    Usa EXCLUSIVAMENTE OpenAI Responses API (GPT-5.x compatible).
    """

    # --------------------------------------------------------
    # 1) Contexto + prompt (tolerante a fallos)
    # --------------------------------------------------------
    try:
        ctx = fetch_context(user_id=payload.user_id)
        system_content = build_prompt(ctx).strip()
    except Exception:
        system_content = (
            "You are Natacha, a cognitive executive assistant. "
            "The memory system is temporarily unavailable. "
            "Proceed safely and explain clearly."
        )

    if not OPENAI_API_KEY:
        return {
            "answer": "⚠️ Falta configurar OPENAI_API_KEY en Cloud Run.",
            "model_called": False,
            "error": "missing_openai_api_key",
        }

    # --------------------------------------------------------
    # 2) Llamada a OpenAI Responses API (GPT-5.2)
    # --------------------------------------------------------
    try:
        response = requests.post(
            OPENAI_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": payload.model or "gpt-5.2",
                "input": [
                    {
                        "role": "system",
                        "content": system_content,
                    },
                    {
                        "role": "user",
                        "content": payload.message,
                    },
                ],
            },
            timeout=30,
        )

        # ---- errores HTTP explícitos
        if response.status_code >= 400:
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{response.status_code}",
                "detail": response.text[:2000],
            }

        data = response.json()

        # ----------------------------------------------------
        # 3) Extraer texto de salida (Responses API)
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
