from typing import Optional
import os
import requests

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-5.2-2025-12-11"


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint cognitivo estable.
    Versión SIN dependencia de memoria/contexto dinámico.
    """

    if not OPENAI_API_KEY:
        return {
            "answer": "⚠️ Falta OPENAI_API_KEY en Cloud Run.",
            "model_called": False,
            "error": "missing_openai_api_key",
        }

    # Prompt base mínimo (estable)
    system_content = (
        "Sos Natacha, un asistente cognitivo ejecutivo. "
        "Respondé de forma clara, estratégica y concreta."
    )

    try:
        resp = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": payload.model,
                "input": [
                    {
                        "role": "system",
                        "content": [{"type": "text", "text": system_content}],
                    },
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": payload.message}],
                    },
                ],
                "max_output_tokens": 256,
            },
            timeout=60,
        )

        if resp.status_code >= 400:
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{resp.status_code}",
                "detail": resp.text[:2000],
            }

        data = resp.json()

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
            "answer": "⚠️ Error interno ejecutando el modelo.",
            "model_called": False,
            "error": "internal_error",
            "detail": str(e),
        }
