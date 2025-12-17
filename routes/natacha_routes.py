
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
    model: Optional[str] = "gpt-4o-mini"


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    try:
        # 1) Contexto + prompt
        ctx = fetch_context(user_id=payload.user_id)
        system_content = build_prompt(ctx).strip()

        if not OPENAI_API_KEY:
            return {
                "answer": "⚠️ Falta OPENAI_API_KEY en Cloud Run.",
                "model_called": False,
                "error": "missing_openai_api_key",
            }

        # 2) Llamada al modelo (NO adivinamos: logueamos status + body)
        url = "https://api.openai.com/v1/chat/completions"

        req_payload = {
            "model": payload.model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": payload.message},
            ],
        }

        try:
            resp = requests.post(
                url,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=req_payload,
                timeout=30,
            )

            # Si OpenAI devuelve 401/403/429/etc, queremos VERLO
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

    except Exception as e:
        return {
            "answer": "⚠️ Error interno preparando contexto/prompt.",
            "model_called": False,
            "error": "internal_error",
            "detail": str(e),
        }

