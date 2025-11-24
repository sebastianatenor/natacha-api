from datetime import datetime
from typing import Optional, Dict, Any, List
import os

import requests
from fastapi import APIRouter, Query

SERVICE_URL = os.getenv(
    "SERVICE_URL",
    "https://natacha-api-422255208682.us-central1.run.app",
)

router = APIRouter(prefix="/natacha", tags=["agenda"])


def _safe_get(url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Helper simple para hacer GETs seguros contra la propia API.
    Nunca levanta excepción: devuelve siempre un dict.
    """
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url, "params": params or {}}


@router.get("/agenda_hoy")
def agenda_hoy(
    user_id: str,
    project: Optional[str] = Query(default=None),
    hours_ahead: int = Query(default=12),
):
    """
    Agenda ejecutiva del día para Sebastián / LLVC.

    Orquesta:
    - summary + highlights desde /memory/engine/context_bundle
    - tareas relevantes desde /tasks/list
    - eventos próximos desde /calendar/proxy/list
    """

    # 1) Contexto ejecutivo (summary + highlights + next_steps)
    ctx_params: Dict[str, Any] = {
        "user_id": user_id,
        "recent_limit": 20,
    }
    if project:
        ctx_params["project"] = project
        ctx_params["semantic_project"] = project
        ctx_params["semantic_q"] = "estado LLVC"
        ctx_params["semantic_limit"] = 5

    ctx = _safe_get(
        f"{SERVICE_URL}/memory/engine/context_bundle",
        params=ctx_params,
    )

    summary_block = ctx.get("summary") or {}
    estado_general = summary_block.get("summary") or "(sin summary)"
    puntos_clave = summary_block.get("highlights") or []
    # 👇 Nuevo: usamos los next_steps del context_bundle
    next_steps: List[str] = summary_block.get("next_steps") or []

    # 2) Tareas relevantes (filtradas por user_id y project)
    tasks_resp = _safe_get(
        f"{SERVICE_URL}/tasks/list",
        params={},
    )
    tasks_items: List[Dict[str, Any]] = tasks_resp.get("items") or []

    tareas_filtradas: List[Dict[str, Any]] = []
    for t in tasks_items:
        if t.get("user_id") != user_id:
            continue
        if project and t.get("project") != project:
            continue
        tareas_filtradas.append(t)

    # Orden: pendientes primero, después por due (si existe)
    def _task_sort_key(t: Dict[str, Any]):
        state = t.get("state") or ""
        due = t.get("due") or "9999-12-31"
        # pending antes que done
        return (0 if state == "pending" else 1, due)

    tareas_filtradas.sort(key=_task_sort_key)

    # === FILTRO INTELIGENTE DE TAREAS (IGNORA SANITY / SISTEMA) ===
    negocio_keywords = [
        "sophie",
        "jamin",
        "xcmg",
        "metalcon",
        "proforma",
        "importación",
        "importacion",
        "grúa",
        "grua",
        "llvc",
    ]

    tareas_relevantes: List[Dict[str, Any]] = []
    for t in tareas_filtradas:
        title_raw = t.get("title") or ""
        title = title_raw.lower()

        # 1) Ignorar tareas internas/técnicas
        if "sanity" in title or "test" in title:
            continue

        # 2) Relevancia de negocio
        es_negocio = any(kw in title for kw in negocio_keywords)

        # 3) Si es de negocio, siempre entra.
        #    Si no es de negocio, entra sólo si está pendiente (ej: reporte financiero).
        if es_negocio or t.get("state") == "pending":
            tareas_relevantes.append(
                {
                    "title": title_raw,
                    "due": t.get("due", ""),
                    "state": t.get("state", ""),
                }
            )

    # 3) Eventos próximos desde Calendar proxy
    cal_resp = _safe_get(
        f"{SERVICE_URL}/calendar/proxy/list",
        params={"hours_ahead": hours_ahead},
    )
    raw_events = cal_resp.get("events", [])
    if isinstance(raw_events, dict):
        # En caso de error estructural, lo dejamos vacío
        raw_events = []

    eventos_hoy = [
        {
            "id": e.get("id"),
            "summary": e.get("summary"),
            "start": e.get("start"),
            "end": e.get("end"),
            "location": e.get("location"),
        }
        for e in raw_events
    ]

    # 4) Recomendación del día
    recomendacion: str
    if next_steps:
        # Si hay próximos pasos de la memoria semántica, los priorizamos.
        recomendacion = next_steps[0]
    elif tareas_relevantes:
        # Priorizar tareas que contengan keywords de negocio
        tareas_negocio = [
            t
            for t in tareas_relevantes
            if any(kw in (t["title"] or "").lower() for kw in negocio_keywords)
        ]
        if tareas_negocio:
            recomendacion = f"Prioridad: {tareas_negocio[0]['title']}"
        else:
            recomendacion = f"Revisar: {tareas_relevantes[0]['title']}"
    else:
        recomendacion = "Hoy no hay tareas pendientes registradas para este proyecto."

    return {
        "status": "ok",
        "user_id": user_id,
        "project": project,
        "estado_general": estado_general,
        "puntos_clave": puntos_clave,
        "proximos_pasos": next_steps,
        "tareas_relevantes": tareas_relevantes,
        "eventos_hoy": eventos_hoy,
        "recomendacion_del_dia": recomendacion,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
