# routes/debug_openai.py

import os
import requests
from fastapi import APIRouter

router = APIRouter(prefix="/debug", tags=["debug"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@router.get("/openai-ping")
def openai_ping():
    """
    Endpoint de diagnóstico puro.
    NO usa memoria, NO usa contexto, NO usa manifests.
    Sirve para verificar conectividad real desde Cloud Run a OpenAI.
    """

    if not OPENAI_API_KEY:
        return {
            "ok": False,
            "error": "missing_openai_api_key"
        }

    try:
        resp = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-5.2",
                "input": "Respondé solo con la palabra OK",
                "max_output_tokens": 32,
            },
            timeout=20,
        )

        return {
            "ok": resp.status_code < 400,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "body_preview": (resp.text or "")[:1000],
        }

    except Exception as e:
        return {
            "ok": False,
            "exception": str(e),
        }
