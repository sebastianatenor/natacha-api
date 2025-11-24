from typing import Optional, Dict, Any, List

from fastapi import APIRouter
from pydantic import BaseModel
import os
import requests

from natacha_brain import (
    fetch_context,
    build_prompt,
    SERVICE_URL,
    search_related_memories,
)

router = APIRouter(prefix="/natacha", tags=["natacha"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ============================================================
# MODELO DE MENSAJE
# ============================================================

class UserMessage(BaseModel):
    user_id: str = "sebastian"
    message: str
    project: Optional[str] = None
    model: Optional[str] = "gpt-4o-mini"


# ============================================================
# AUTO MEMORY HELPERS
# ============================================================

def _should_store_message(msg: str) -> bool:
    """
    Decide si una frase del usuario debe guardarse como memoria.
    """
    if not msg:
        return False

    trivial = ["hola", "dale", "ok", "si", "sí", "gracias"]
    if msg.lower().strip() in trivial:
        return False

    keywords = ["sophie", "jamin", "grúa", "llvc", "china", "importación"]
    return any(k in msg.lower() for k in keywords)


def _store_raw_memory(user_id: str, note: str, project: Optional[str] = None):
    """
    Guarda memoria en:
    - /memory/engine/raw
    - /memory/v2/store
    """
    try:
        base = SERVICE_URL.rstrip("/")
        project_value = project or "general"

        # memoria cruda
        requests.post(
            f"{base}/memory/engine/raw",
            json={
                "user_id": user_id,
                "note": note,
                "kind": "conversation",
                "importance": "normal",
                "source": "natacha-auto",
                "project": project_value,
            },
            timeout=5,
        )

        # memoria semántica v2
        tags = [
            "conversation",
            "natacha-auto",
            f"user:{user_id}",
            f"project:{project_value}",
        ]

        requests.post(
            f"{base}/memory/v2/store",
            json={
                "items": [
                    {
                        "text": note,
                        "tags": tags,
                        "meta": {
                            "user_id": user_id,
                            "kind": "conversation",
                            "source": "natacha-auto",
                            "project": project_value,
                        },
                    }
                ]
            },
            timeout=5,
        )

    except Exception:
        pass  # nunca romper el flujo


# ============================================================
# AGENDA HOY – FETCH AUTOMÁTICO
# ============================================================

def _maybe_fetch_agenda_block(user_id: str, message: str) -> str:
    """
    Si el mensaje habla de agenda, prioridades, qué hacer hoy,
    se consulta /natacha/agenda_hoy y se genera un bloque de contexto.
    """
    try:
        msg = (message or "").lower()

        triggers = [
            "agenda de hoy",
            "que tengo que hacer hoy",
            "qué tengo que hacer hoy",
            "prioridad de hoy",
            "prioridades de hoy",
            "que hago hoy",
            "qué hago hoy",
            "agenda ejecutiva",
        ]

        if not any(t in msg for t in triggers):
            return ""

        base = SERVICE_URL.rstrip("/")
        url = f"{base}/natacha/agenda_hoy"

        resp = requests.get(
            url,
            params={"user_id": user_id, "project": "LLVC", "hours_ahead": 12},
            timeout=8,
        )
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

        recomendacion = data.get("recomendacion_del_dia") or ""
        proximos = data.get("proximos_pasos") or []
        tareas = data.get("tareas_relevantes") or []
        eventos = data.get("eventos_hoy") or []

        lines: List[str] = []
        lines.append("[INSTRUCCIONES PARA RESPONDER SOBRE LA AGENDA DE HOY]")
        lines.append("1) Empezá con prioridad principal del día.")
        lines.append("2) Luego bullets de próximos pasos.")
        lines.append("3) Mencionar tareas y eventos si existen.")
        lines.append("4) Cerrar con acción sugerida.\n")

        lines.append("[AGENDA EJECUTIVA GENERADA POR /natacha/agenda_hoy]")

        if recomendacion:
            lines.append(f"- Recomendación del día: {recomendacion}")

        if proximos:
            lines.append("- Próximos pasos sugeridos:")
            for p in proximos:
                lines.append(f"  • {p}")

        if tareas:
            lines.append("- Tareas relevantes:")
            for t in tareas[:5]:
                title = t.get("title", "")
                due = t.get("due") or ""
                state = t.get("state") or ""
                suffix = f" (vence: {due})" if due else ""
                lines.append(f"  • [{state}] {title}{suffix}")

        if eventos:
            lines.append("- Eventos próximos:")
            for e in eventos[:3]:
                title = e.get("summary") or ""
                start = e.get("start") or ""
                loc = e.get("location") or ""
                loc_txt = f" @ {loc}" if loc else ""
                lines.append(f"  • {start}: {title}{loc_txt}")

        return "\n\n" + "\n".join(lines) + "\n"

    except Exception:
        return ""


# ============================================================
# ENDPOINT PRINCIPAL: /natacha/respond
# ============================================================

@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Conversación principal con Natacha.
    Incluye memoria, contexto, semántica v2 y agenda si aplica.
    """
    try:
        # 1) Contexto general
        ctx = fetch_context(
            user_id=payload.user_id,
            project=payload.project or "LLVC",
        )

        base_prompt = build_prompt(ctx, payload.message)

        # 2) Guardar memoria si corresponde
        try:
            if _should_store_message(payload.message):
                _store_raw_memory(
                    payload.user_id,
                    payload.message,
                    payload.project or "LLVC",
                )
        except Exception:
            pass

        # 3) Memoria semántica v2
        related_block = ""
        try:
            related_info: Dict[str, Any] = search_related_memories(
                user_id=payload.user_id,
                project=payload.project or "LLVC",
                message=payload.message,
                limit=5,
            )

            if isinstance(related_info, dict):
                semantic_v2_block = related_info.get("result") or {}
                sem_result = semantic_v2_block.get("result") or {}
                items = sem_result.get("items") or []

                bullets = []
                for it in items:
                    if isinstance(it, dict):
                        txt = it.get("text") or ""
                        if txt:
                            bullets.append(f"- {txt}")

                if bullets:
                    related_block = (
                        "\n\n[MEMORIA RELEVANTE v2]\n" + "\n".join(bullets) + "\n"
                    )
        except Exception:
            pass

        # 4) Agenda si aplica
        agenda_block = _maybe_fetch_agenda_block(payload.user_id, payload.message)

        # 5) Armar prompt final
        final_prompt = base_prompt + related_block + agenda_block

        if not OPENAI_API_KEY:
            return {
                "answer": "(No OPENAI_API_KEY) Prompt generado.",
                "used_prompt": final_prompt,
                "model_called": False,
            }

        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)

        completion = client.chat.completions.create(
            model=payload.model,
            messages=[
                {"role": "system", "content": final_prompt},
                {"role": "user", "content": payload.message},
            ],
        )

        answer = completion.choices[0].message.content

        return {
            "answer": answer,
            "used_prompt": final_prompt,
            "model_called": True,
        }

    except Exception as e:
        return {
            "error": repr(e),
            "message": payload.message,
            "model_called": False,
        }


# ============================================================
# HEALTHCHECK
# ============================================================

@router.get("/healthcheck")
def natacha_healthcheck():
    return {"status": "ok", "component": "natacha-routes"}
