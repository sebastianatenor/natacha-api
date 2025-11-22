#!/usr/bin/env python3
"""
exec_status.py

Tablero ejecutivo rápido para Sebastián:
- Chequea /health (API)
- Chequea /natacha/healthcheck (cerebro y memoria)
- Lista tareas LLVC con conteo por urgencia (usando misma lógica que tasks_urgency.py)
"""

import os
import sys
import argparse
import json
import datetime as dt
from typing import Any, Dict, List, Tuple

import requests

BASE = os.getenv("BASE", "https://natacha-api-422255208682.us-central1.run.app")


# ============================================================
# Helpers de urgencia (copiados de tasks_urgency.py)
# ============================================================
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


def fetch_tasks_for(user_id: str, project: str) -> List[Dict[str, Any]]:
    """
    Llama a /tasks/list SIN filtros y filtra en cliente por user_id + project.
    """
    url = f"{BASE}/tasks/list"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    items = data.get("items", [])

    filtered: List[Dict[str, Any]] = []
    for t in items:
        if t.get("user_id") != user_id:
            continue
        if t.get("project") != project:
            continue
        score, level = compute_urgency(t)
        t2 = dict(t)
        t2["urgency_score"] = score
        t2["urgency"] = level
        filtered.append(t2)

    filtered.sort(key=lambda x: x["urgency_score"], reverse=True)
    return filtered


# ============================================================
# Chequeos de infra y cerebro
# ============================================================

def check_health() -> Tuple[bool, Dict[str, Any]]:
    url = f"{BASE}/health"
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        data = r.json()
        ok = str(data.get("status", "")).lower() == "ok"
        return ok, data
    except Exception as e:
        return False, {"error": str(e)}


def check_natacha_health(user_id: str, project: str) -> Tuple[bool, Dict[str, Any]]:
    url = f"{BASE}/natacha/healthcheck"
    payload = {"user_id": user_id, "project": project}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "ok":
            return False, data
        checks = data.get("checks", {})
        all_ok = all(bool(v) for v in checks.values()) if isinstance(checks, dict) else False
        return all_ok, data
    except Exception as e:
        return False, {"error": str(e)}


# ============================================================
# Presentación
# ============================================================

def print_status(user_id: str, project: str, as_json: bool) -> None:
    api_ok, api_data = check_health()
    brain_ok, brain_data = check_natacha_health(user_id, project)

    try:
        tasks = fetch_tasks_for(user_id, project)
    except Exception as e:
        tasks = []
        tasks_error = str(e)
    else:
        tasks_error = ""

    if as_json:
        out = {
            "base": BASE,
            "user_id": user_id,
            "project": project,
            "api": {
                "ok": api_ok,
                "data": api_data,
            },
            "natacha_brain": {
                "ok": brain_ok,
                "checks": brain_data.get("checks"),
                "meta": brain_data.get("meta"),
            },
            "tasks": {
                "error": tasks_error or None,
                "count": len(tasks),
                "items": tasks,
            },
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return

    # --- Modo humano / tabla ---
    print(f"Base: {BASE}")
    print(f"user_id: {user_id} | project: {project}")
    print("=" * 70)
    print("INFRA / API")
    print("-" * 70)
    print(f"API /health:        {'OK ✅' if api_ok else 'ERROR ❌'}")
    if not api_ok:
        print(f"  Detalle: {api_data.get('error', api_data)}")
    print()

    print("CEREBRO / CONTEXTO Natacha")
    print("-" * 70)
    print(f"/natacha/healthcheck: {'OK ✅' if brain_ok else 'WARN ⚠️'}")
    checks = brain_data.get("checks", {}) if isinstance(brain_data, dict) else {}
    if checks:
        for k, v in checks.items():
            flag = "✅" if v else "⚠️"
            print(f"  {k}: {flag}")
    else:
        print("  (sin datos de checks)")

    print()
    print("TAREAS LLVC (ordenadas por urgencia)")
    print("-" * 70)
    if tasks_error:
        print(f"ERROR al obtener tareas: {tasks_error}")
    else:
        print(f"Total tareas: {len(tasks)}")
        print(f"{'URGENCIA':<7} {'SCORE':<5} {'STATE':<8} {'DUE':<12} {'TÍTULO'}")
        print("-" * 70)
        for t in tasks[:10]:
            due = str(t.get("due", ""))[:12]
            print(
                f"{t['urgency']:<7} {t['urgency_score']:<5} {t.get('state',''):<8} {due:<12} {t.get('title','')}"
            )


def main() -> None:
    parser = argparse.ArgumentParser(description="Tablero ejecutivo rápido de Natacha para LLVC.")
    parser.add_argument("--user", required=True, help="user_id (ej: sebastian)")
    parser.add_argument("--project", required=True, help="project (ej: LLVC)")
    parser.add_argument("--json", action="store_true", help="Salida en JSON")
    args = parser.parse_args()

    print_status(args.user, args.project, as_json=args.json)


if __name__ == "__main__":
    main()
