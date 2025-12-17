from typing import Optional, Any, Dict
import os
import requests

from fastapi import APIRouter
from pydantic import BaseModel

from natacha_brain import fetch_context, build_prompt

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
NATACHA_MODEL = os.getenv("NATACHA_MODEL", "gpt-5.2-chat-latest")  # estable “latest”
MAX_OUTPUT_TOKENS = int(os.getenv("NATACHA_MAX_OUTPUT_TOKENS", "512"))  # >= 16


class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = None


def _extract_output_text(resp_json: Dict[str, Any]) -> str:
    """
    Responses API devuelve:
      - output: [{type:"message", content:[{type:"output_text", text:"..."}]}]
    """
    try:
        out = resp_json.get("output") or []
        for item in out:
            if item.get("type") == "message":
                parts = item.get("content") or []
                texts = []
                for p in parts:
                    if p.get("type") in ("output_text", "text"):
                        t = p.get("text") or ""
                        if t:
                            texts.append(t)
                if texts:
                    return "\n".join(texts).strip()
        # fallback viejo/cómodo si existe
        if isinstance(resp_json.get("text"), dict):
            return ""
    except Exception:
        pass
    return ""


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    # 1) Preparar contexto/prompt, tolerante a fallas
    try:
        ctx = fetch_context(user_id=payload.user_id)
    except Exception as e:
        ctx = {}
        # no cortamos, solo registramos debug de salida
        ctx["_context_error"] = str(e)

    try:
        system_content = (build_prompt(ctx) or "").strip()
    except Exception as e:
        system_content = ""
        # seguimos sin romper
        system_content = (
            "You are Natacha, an executive cognitive assistant for LLVC.\n"
            "Be concise, practical, and safe.\n"
            f"[build_prompt_error]: {str(e)}"
        )

    if not OPENAI_API_KEY:
        return {
            "answer": "⚠️ Falta OPENAI_API_KEY en Cloud Run.",
            "model_called": False,
            "error": "missing_openai_api_key",
        }

    model = (payload.model or NATACHA_MODEL).strip()
    user_text = (payload.message or "").strip()

    # 2) Llamar a OpenAI Responses API
    try:
        url = f"{OPENAI_BASE_URL.rstrip('/')}/responses"
        req_payload = {
            "model": model,
            "max_output_tokens": max(MAX_OUTPUT_TOKENS, 16),
            "input": [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_text},
            ],
        }

        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=req_payload,
            timeout=45,
        )

        if resp.status_code >= 400:
            body = (resp.text or "")[:4000]
            return {
                "answer": "⚠️ Error al llamar al modelo externo.",
                "model_called": False,
                "error": f"openai_http_{resp.status_code}",
                "detail": body,
                "debug": {
                    "model": model,
                    "endpoint": "/responses",
                },
            }

        data = resp.json()
        answer = _extract_output_text(data)

        if not answer:
            return {
                "answer": "⚠️ OpenAI respondió pero no pude extraer texto.",
                "model_called": False,
                "error": "openai_parse_empty",
                "detail": str(data)[:4000],
                "debug": {"model": model},
            }

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
            "debug": {"model": model},
        }
