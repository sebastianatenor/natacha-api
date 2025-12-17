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


class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-5.2-2025-12-11"


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    try:
        # 1) Contexto (tolerante a fallos)
        try:
            ctx = fetch_context(user_id=payload.user_id)
        except Exception:
            ctx = {}

        # 2) Prompt base
        system_content = build_prompt(ctx).strip()

        if not OPENAI_API_KEY:
            return {
                "answer": "⚠️ Falta OPENAI_API_KEY en Cloud Run.",
                "model_called": False,
                "error": "missing_openai_api_key",
            }

        # 3) OpenAI Responses API (GPT-5.2)
        url = "https://api.openai.com/v1/responses"

        req_payload = {
            "model": payload.model or "gpt-5.2-2025-12-11",
            "input": [
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": system_content}
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": payload.message}
                    ],
                },
            ],
            # 🔴 CLAVE DEL FIX
            "max_output_tokens": 256,
        }

        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=req_payload,
            timeout=60,
        )

        if resp.status_code >= 400:
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{resp.status_code}",
                "detail": (resp.text or "")[:2000],
            }

        data = resp.json()

        # Extraer texto de Responses API
        answer_text = ""
        for item in data.get("output", []):
            if item.get("type") == "message":
                for block in item.get("content", []):
                    if block.get("type") == "output_text":
                        answer_text += block.get("text", "")

        return {
            "answer": answer_text.strip(),
            "model_called": True,
            "error": None,
        }

    except Exception as e:
        return {
            "answer": "⚠️ Error interno preparando contexto o respuesta.",
            "model_called": False,
            "error": "internal_error",
            "detail": str(e),
        }
