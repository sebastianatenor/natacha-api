#!/usr/bin/env python3
"""
tasks_urgency.py

Evalúa la urgencia de las tareas de Natacha para un user_id + project
usando /tasks/list SIN filtros en la API y filtrando del lado del cliente.
"""

import os
import sys
import argparse
import json
import datetime as dt
from typing import List, Dict, Any, Tuple

import requests

BASE = os.getenv("BASE", "https://natacha-api-422255208682.us-central1.run.app")


def fetch_tasks_raw() -> List[Dict[str, Any]]:
    """
    Llama a /tasks/list SIN query params.
    El endpoint con filtros está tirando 500 en Cloud Run, así que evitamos eso.
    """
    url = f"{BASE}/tasks/list"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("items", [])


def filter_tasks(tasks: List[Dict[str, Any]], user_id: str, project: str) -> List[Dict[str, Any]]:
    """
    Filtra las tareas en memoria por user_id y project.
    """
    out: List[Dict[str, Any]] = []
    for t in tasks:
        if t.get("user_id") != user_id:
            continue
        if t.get("project") != project:
            continue
        out.append(t)
    return out


def compute_urgency(task: Dict[str, Any]) -> Tuple[int, str]:
    """
    Calcula un score de urgencia simple + etiqueta ALTA / MEDIA / BAJA.
    """
    state = (task.get("state") or "").lower()
    due_raw = task.get("due") or ""
    title = task.get("title") or ""
    detail = task.get("detail") or ""
    text = f"{title} {detail}".lower()

    score = 0

    # 1) Base según estado
    if state in ("done", "cancelled"):
        score = 0
    else:
        score = 30  # cualquier tarea pendiente parte de una urgencia media

    # 2) Bonus por fecha de vencimiento
    if due_raw:
        try:
            if "T" in due_raw:
                # Formato tipo ISO con hora
                due_dt = dt.datetime.fromisoformat(due_raw.replace("Z", ""))
            else:
                # Solo fecha YYYY-MM-DD
                due_dt = dt.datetime.fromisoformat(due_raw)
            today = dt.date.today()
            days = (due_dt.date() - today).days

            if days <= 0:       # vencida o hoy
                score += 40
            elif days <= 3:
                score += 20
            elif days <= 7:
                score += 10
        except Exception:
            # Si no se puede parsear, simplemente ignoramos la fecha
            pass

    # 3) Bonus por palabras clave importantes para LLVC ahora
    if any(k in text for k in ["sophie", "jamin", "proforma", "grúa", "gruas", "grúas", "sqz"]):
        score += 20
    if "metalcon" in text:
        score += 10
    if "financ" in text:
        score += 10

    # 4) Etiqueta de urgencia
    if score >= 70:
        level = "ALTA"
    elif score >= 30:
        level = "MEDIA"
    else:
        level = "BAJA"

    return score, level


def print_table(tasks: List[Dict[str, Any]], user_id: str, project: str) -> None:
    print(f"Base: {BASE}")
    print(f"user_id: {user_id}")
    print(f"project: {project}")
    print(f"Total tareas filtradas: {len(tasks)}")
    print()
    print(f"{'URGENCIA':<7} {'SCORE':<5} {'STATE':<8} {'DUE':<12} {'TÍTULO'}")
    print("-" * 80)
    for t in tasks:
        due = str(t.get("due", ""))[:12]
        print(
            f"{t['urgency']:<7} {t['urgency_score']:<5} {t.get('state',''):<8} {due:<12} {t.get('title','')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Evalúa urgencia de tareas para un usuario/proyecto.")
    parser.add_argument("--user", required=True, help="user_id (ej: sebastian)")
    parser.add_argument("--project", required=True, help="project (ej: LLVC)")
    parser.add_argument("--json", action="store_true", help="Salida en JSON en lugar de tabla")
    args = parser.parse_args()

    user_id = args.user
    project = args.project

    try:
        raw_tasks = fetch_tasks_raw()
    except requests.HTTPError as e:
        print(
            f"ERROR al obtener tareas desde {BASE}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)

    tasks = filter_tasks(raw_tasks, user_id=user_id, project=project)

    enriched: List[Dict[str, Any]] = []
    for t in tasks:
        score, level = compute_urgency(t)
        t2 = dict(t)
        t2["urgency_score"] = score
        t2["urgency"] = level
        enriched.append(t2)

    # Ordenar por urgencia descendente
    enriched.sort(key=lambda x: x["urgency_score"], reverse=True)

    if args.json:
        output = {
            "base": BASE,
            "user_id": user_id,
            "project": project,
            "count": len(enriched),
            "items": enriched,
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print_table(enriched, user_id=user_id, project=project)


if __name__ == "__main__":
    main()
