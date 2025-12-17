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
    Núcleo conversacional ESTABLE de Natacha.
    """

    try:
        # 1) Contexto cognitivo
        ctx = fetch_context(user_id=payload.user_id)

        # 2) Prompt
        system_content = build_prompt(ctx).strip()
        full_prompt = system_content + f"\n\nUser message:\n{payload.message}"

        # 3) Sin API key → diagnóstico
        if not OPENAI_API_KEY:
            return {
                "answer": (
                    "⚠️ OPENAI_API_KEY no configurada.\n\n"
                    f"{full_prompt}"
                ),
                "model_called": False,
                "error": "missing_openai_api_key",
            }

        # 4) Chat Completions (estable)
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
                "model_called": True,
                "error": None,
            }

        except Exception as e:
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": str(e),
            }

    except Exception as e:
        return {
            "answer": "⚠️ Error interno preparando el contexto.",
            "model_called": False,
            "error": str(e),
        }
