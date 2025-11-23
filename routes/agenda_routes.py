from fastapi import APIRouter, Query
import requests
import os
from datetime import datetime

router = APIRouter(prefix="/natacha", tags=["agenda"])

SERVICE_URL = os.getenv(
    "SERVICE_URL",
    "https://natacha-api-422255208682.us-central1.run.app"
)

CALENDAR_URL = "https://natacha-calendar-service-422255208682.us-central1.run.app/calendar/demo-events"


def _safe_get(url, params=None):
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url}


@router.get("/agenda_hoy")
def agenda_hoy(
    user_id: str = Query(...),
    project: str = Query(None)
):
    """
    Agenda ejecutiva del día para Sebastián:
    - summary del context_bundle
    - tareas relevantes
    - eventos de hoy (vía Calendar demo)
    """

    # === 1) Summary ejecutivo desde context_bundle ===
    ctx = _safe_get(
        f"{SERVICE_URL}/memory/engine/context_bundle",
        params={
            "user_id": user_id,
            "project": project,
            "semantic_project": project,
            "semantic_q": "estado LLVC",
            "semantic_limit": 5
        }
    )

    summary_text = ctx.get("summary", {}).get("summary", "(sin summary)")
    highlights = ctx.get("summary", {}).get("highlights", [])
    next_steps = ctx.get("summary", {}).get("next_steps", [])

    # === 2) Tareas ===
    tasks_raw = _safe_get(f"{SERVICE_URL}/tasks/list")

    tasks_list = []
    if isinstance(tasks_raw, dict) and tasks_raw.get("status") == "ok":
        for t in tasks_raw.get("items", []):
            if t.get("project") == project:
                tasks_list.append({
                    "title": t.get("title"),
                    "due": t.get("due"),
                    "state": t.get("state"),
                })

    # === 3) Eventos del día (demo) ===
    cal_raw = _safe_get(CALENDAR_URL)
    eventos_hoy = []

    if isinstance(cal_raw, list):
        for ev in cal_raw:
            try:
                start = datetime.fromisoformat(ev["start"])
                if start.date() == datetime.utcnow().date():
                    eventos_hoy.append({
                        "id": ev.get("id"),
                        "summary": ev.get("summary"),
                        "start": ev.get("start"),
                        "end": ev.get("end"),
                        "location": ev.get("location"),
                    })
            except Exception:
                pass

    # === 4) Recomendación ejecutiva ===
    recomendacion = None
    if next_steps:
        recomendacion = next_steps[0]
    elif tasks_list:
        recomendacion = f"Revisar: {tasks_list[0]['title']}"

    return {
        "status": "ok",
        "user_id": user_id,
        "project": project,
        "estado_general": summary_text,
        "puntos_clave": highlights,
        "tareas_relevantes": tasks_list,
        "eventos_hoy": eventos_hoy,
        "recomendacion_del_dia": recomendacion,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
