from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    """Parsea un ISO8601 simple; si falla, devuelve None."""
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    # Sacamos sufijo Z si viene
    if text.endswith("Z"):
        text = text[:-1]
    try:
        return datetime.fromisoformat(text)
    except Exception:
        return None


def _sort_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ordena tareas por:
    1) las que tienen due primero
    2) fecha de due más cercana
    3) como fallback, created_at si existe
    """
    def _key(t: Dict[str, Any]):
        due_dt = _parse_iso(t.get("due"))
        created_dt = _parse_iso(t.get("created_at"))
        # Las que NO tienen due van al final
        has_due = 0 if due_dt else 1
        # usamos created_at solo como fallback visual
        return (
            has_due,
            due_dt or datetime.max,
            created_dt or datetime.max,
        )

    return sorted(tasks, key=_key)


def _pick_primary_pending_task(pending: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Elige la tarea pendiente 'principal' (la primera según el orden)."""
    if not pending:
        return None
    ordered = _sort_tasks(pending)
    return ordered[0]


def _pick_recent_topic(memories: List[Dict[str, Any]], project: Optional[str]) -> Optional[str]:
    """
    Toma el primer summary razonable del proyecto (o global si no hay project).
    """
    for m in memories:
        if project and m.get("project") not in (project, None, ""):
            continue
        text = (m.get("summary") or "").strip() or (m.get("detail") or "").strip()
        if text:
            return text
    # Fallback: cualquier memoria con summary
    for m in memories:
        text = (m.get("summary") or "").strip()
        if text:
            return text
    return None


def _pick_next_event(events: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Dado un listado de eventos con campo 'start' en ISO, elige el próximo.
    Si no hay eventos o no tienen fecha legible, devuelve None.
    """
    if not events:
        return None

    def _key(ev: Dict[str, Any]):
        start = ev.get("start") or ev.get("start_time")
        dt = _parse_iso(start)
        return dt or datetime.max

    ordered = sorted(events, key=_key)
    first = ordered[0]
    start_dt = _parse_iso(first.get("start") or first.get("start_time"))
    if not start_dt or start_dt == datetime.max:
        return None
    return first


def build_context_bundle(
    user_id: Optional[str],
    project: Optional[str],
    memories: List[Dict[str, Any]],
    tasks: List[Dict[str, Any]],
    events: List[Dict[str, Any]],
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Motor de contexto v2 (puro, sin Firestore dentro):
    - recibe memorias, tareas y eventos ya cargados
    - devuelve un bundle con:
        summary, tasks, events, raw
    """
    # --- Tareas: separamos pendientes y hechas ---
    pending_tasks = [
        t for t in tasks
        if (t.get("state") or "").lower() == "pending"
    ]
    done_tasks = [
        t for t in tasks
        if (t.get("state") or "").lower() == "done"
    ]

    pending_sorted = _sort_tasks(pending_tasks)
    done_sorted = _sort_tasks(done_tasks)

    primary_task = _pick_primary_pending_task(pending_sorted)
    topic = _pick_recent_topic(memories, project)
    next_event = _pick_next_event(events)

    # --- Headline ejecutivo ---
    parts: List[str] = []
    if project:
        parts.append(f"Proyecto foco: {project}.")
    if primary_task:
        parts.append(f"Prioridad operativa: {primary_task.get('title')}.")
    if topic:
        parts.append(f"Tema reciente: {topic}.")
    if next_event:
        parts.append(f"Próximo evento: {next_event.get('summary')}.")
    headline = " ".join(parts) if parts else "Contexto operativo listo."

    summary = {
        "headline": headline,
        "user_id": user_id,
        "project": project,
        "pending_task_count": len(pending_tasks),
        "done_task_count": len(done_tasks),
        "event_count": len(events),
        "recent_memory_count": len(memories),
    }

    # --- Bloque de tareas ---
    tasks_block = {
        "pending": pending_sorted[:limit],
        "done_recent": done_sorted[:limit],
    }

    # --- Bloque de eventos ---
    events_block = {
        "items": events,
        "next_event": next_event,
        "count": len(events),
    }

    raw_block = {
        "memories": memories[:limit],
        "task_count": len(tasks),
        "event_count": len(events),
    }

    return {
        "summary": summary,
        "tasks": tasks_block,
        "events": events_block,
        "raw": raw_block,
    }
