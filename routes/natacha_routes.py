from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
import os
import requests

from natacha_brain import fetch_context, build_prompt

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    model: Optional[str] = "gpt-4o-mini"


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint principal de Natacha:

    1. Pide contexto al motor de memoria (/memory/engine/context_bundle) vía natacha_brain.fetch_context
    2. Construye el prompt base con memoria + reglas vía natacha_brain.build_prompt
    3. Agrega el mensaje del usuario
    4. Si hay OPENAI_API_KEY, llama al modelo externo; si no, devuelve el prompt que usaría
    5. TODOS los errores se devuelven en JSON (no hay más 'Internal Server Error' plano)
    """

    try:
        # 1) Traer contexto desde el motor de memoria
        ctx = fetch_context(user_id=payload.user_id)

        # 2) Construir el prompt con memoria + mensaje actual
        base_prompt = build_prompt(ctx)
        full_prompt = base_prompt + f"\n\nUser message:\n{payload.message}"

        # 3) Si no hay OPENAI_API_KEY, devolvemos el prompt y un aviso
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

        # 4) Intentar llamar al modelo externo (OpenAI u otro compatible)
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
                        {"role": "system", "content": base_prompt},
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
                "used_prompt": base_prompt,
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
