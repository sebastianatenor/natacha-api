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
    Define si el mensaje del usuario es relevante como memoria.
    Más adelante se puede expandir con reglas más avanzadas.
    """
    if not msg:
        return False

    # evitar guardar mensajes triviales
    trivial = ["hola", "dale", "ok", "si", "sí", "gracias"]
    if msg.lower().strip() in trivial:
        return False

    # si menciona temas del negocio, lo guardamos
    keywords = ["Sophie", "Jamin", "grúa", "China", "LLVC", "importación", "vial"]
    if any(k.lower() in msg.lower() for k in keywords):
        return True

    return False


def _store_raw_memory(user_id: str, note: str, project: Optional[str] = None):
    """
    Llama al motor de memoria para guardar automáticamente la conversación.
    - Guarda memoria cruda en /memory/engine/raw
    - Guarda memoria v2 en /memory/v2/store para búsquedas semánticas
    Ignora errores silenciosamente para no romper el flujo.
    """
    try:
        base = SERVICE_URL.rstrip("/")
        project_value = project or "general"

        # 1) memoria cruda normalizada
        url_raw = f"{base}/memory/engine/raw"
        payload_raw = {
            "user_id": user_id,
            "note": note,
            "kind": "conversation",
            "importance": "normal",
            "source": "natacha-auto",
            "project": project_value,
        }
        requests.post(url_raw, json=payload_raw, timeout=5)

        # 2) memoria v2 para búsquedas semánticas
        url_v2 = f"{base}/memory/v2/store"
        tags = [
            "conversation",
            "natacha-auto",
            f"user:{user_id}",
        ]
        if project:
            tags.append(f"project:{project_value}")

        payload_v2 = {
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
        }
        requests.post(url_v2, json=payload_v2, timeout=5)

    except Exception:
        # nunca romper la conversación por un problema de memoria
        pass


# ============================================================
# AGENDA EJECUTIVA – INTEGRACIÓN CON /natacha/agenda_hoy
# ============================================================


def _maybe_fetch_agenda_block(user_id: str, message: str) -> str:
    """
    Si el usuario está preguntando por su agenda / qué hacer hoy / prioridades,
    consultamos /natacha/agenda_hoy y agregamos un bloque estructurado al prompt.

    Esto NO rompe nada si falla: simplemente devuelve "".
    """
    try:
        msg = (message or "").lower()

        triggers = [
            "agenda de hoy",
            "qué tengo que hacer hoy",
            "que tengo que hacer hoy",
            "prioridad de hoy",
            "prioridades de hoy",
            "qué es lo más importante hoy",
            "que es lo mas importante hoy",
            "que hago hoy",
            "qué hago hoy",
        ]

        if not any(t in msg for t in triggers):
            return ""

        base = SERVICE_URL.rstrip("/")
        url = f"{base}/natacha/agenda_hoy"

        # Por ahora asumimos el proyecto LLVC como default del usuario
        resp = requests.get(
            url,
            params={"user_id": user_id, "project": "LLVC", "hours_ahead": 12},
            timeout=8,
        )
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()

        recomendacion = data.get("recomendacion_del_dia") or ""
        proximos: List[str] = data.get("proximos_pasos") or []
        tareas: List[Dict[str, Any]] = data.get("tareas_relevantes") or []
        eventos: List[Dict[str, Any]] = data.get("eventos_hoy") or []

        lines: List[str] = []

        # Instrucciones de formato para el modelo
        lines.append(
            "[INSTRUCCIONES PARA RESPONDER SOBRE LA AGENDA DE HOY]\n"
            "Cuando el usuario pregunte por su agenda, qué hacer hoy o prioridades:\n"
            "1) Empezá con una frase corta con la prioridad principal del día.\n"
            "2) Luego lista en bullets los próximos pasos concretos.\n"
            "3) Después, si aplica, menciona las tareas relevantes y los eventos próximos.\n"
            "4) Cerrá con una propuesta de 'siguiente movimiento' claro y accionable.\n"
        )

        lines.append("[AGENDA EJECUTIVA GENERADA POR /natacha/agenda_hoy]")

        if recomendacion:
            lines.append(f"- Recomendación del día: {recomendacion}")

        if proximos:
            lines.append("- Próximos pasos sugeridos:")
            for p in proximos:
                if p:
                    lines.append(f"  • {p}")

        if tareas:
            lines.append("- Tareas relevantes (pendientes y de negocio):")
            for t in tareas[:5]:
                title = t.get("title", "")
                due = t.get("due") or ""
                state = t.get("state") or ""
                suffix = f" (vence: {due})" if due else ""
                lines.append(f"  • [{state}] {title}{suffix}")

        if eventos:
            lines.append("- Eventos próximos en calendario:")
            for e in eventos[:3]:
                title = e.get("summary") or ""
                start = e.get("start") or ""
                location = e.get("location") or ""
                loc_suffix = f" @ {location}" if location else ""
                lines.append(f"  • {start}: {title}{loc_suffix}")

        # Si por alguna razón no hay nada útil, no agregamos bloque
        contenido = "\n".join([ln for ln in lines if ln.strip()])
        if not contenido.strip():
            return ""

        return "\n\n" + contenido

    except Exception:
        # Nunca romper el flujo por agenda
        return ""


@router.post("/respond")
def natacha_respond(payload: UserMessage):
    """
    Endpoint principal de Natacha:

    1. Pide contexto al motor de memoria (/memory/engine/context_bundle) vía natacha_brain.fetch_context
    2. Construye el prompt base con memoria + reglas vía natacha_brain.build_prompt
    3. Busca memorias v2 relacionadas al mensaje actual
    4. Agrega el mensaje del usuario
    5. Si hay OPENAI_API_KEY, llama al modelo externo; si no, devuelve el prompt que usaría
    6. TODOS los errores se devuelven en JSON (no hay más 'Internal Server Error' plano)
    """

    try:
        # 1) Traer contexto desde el motor de memoria (con project si existe)
        ctx = fetch_context(
            user_id=payload.user_id,
            project=payload.project or "LLVC",
        )

        # 2) Construir el prompt con memoria consolidada (+ mensaje actual)
        base_prompt = build_prompt(ctx, payload.message)

        # 2b) Guardar memoria de conversación si aplica
        try:
            if _should_store_message(payload.message):
                project_value = payload.project or "LLVC"
                _store_raw_memory(payload.user_id, payload.message, project_value)
        except Exception:
            # Nunca romper la respuesta por un problema de memoria
            pass

        # 3) Buscar memorias semánticamente relacionadas al mensaje actual (v2)
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
                # semantic_v2_block es lo que vendría en ctx["semantic_v2"]
                sem_result = semantic_v2_block.get("result") or {}
                items = sem_result.get("items") or []

                bullets: List[str] = []
                for it in items:
                    if not isinstance(it, dict):
                        continue
                    text = (
                        it.get("text")
                        or it.get("summary")
                        or it.get("note")
                        or ""
                    )
                    text = (text or "").strip()
                    if text:
                        bullets.append(f"- {text}")

                if bullets:
                    related_block = (
                        "\n\nMemoria relevante para este mensaje (v2 – items):\n"
                        + "\n".join(bullets)
                    )

        except Exception:
            # si falla la búsqueda semántica, seguimos sin cortar
            related_block = ""

        # 3b) Bloque de agenda ejecutiva (si el mensaje lo dispara)
        agenda_block = _maybe_fetch_agenda_block(payload.user_id, payload.message)

        # 4) Prompt completo que se habría usado
        system_content = (base_prompt + related_block + agenda_block).strip()
        full_prompt = system_content + f"\n\nUser message:\n{payload.message}"

        # 5) Si no hay OPENAI_API_KEY, devolvemos el prompt y un aviso
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

        # 6) Intentar llamar al modelo externo (OpenAI u otro compatible)
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
                "used_prompt": system_content,
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
        # Error general del endpoint Natacha
        return {
            "answer": (
                "⚠️ Hubo un error interno al procesar la solicitud de Natacha. "
                "Revisá los logs del backend para más detalle."
            ),
            "used_prompt": "",
            "model_called": False,
            "error": "natacha_internal_error",
            "detail": str(e),
        }
