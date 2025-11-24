#!/usr/bin/env python3
"""
daily_starter.py — Agenda ejecutiva v2 con engine semántico

- Llama a /memory/engine/context_bundle_v2
- Muestra:
  * Prioridad absoluta del día (headline)
  * Tareas pendientes principales (ordenadas por engine v2)
  * Eventos relevantes (si el bundle trae eventos)

Uso típico:

  BASE="https://natacha-api-mkwskljrhq-uc.a.run.app" \\
    python3 scripts/daily_starter.py --user sebastian --project LLVC --limit 10
"""

import os
import sys
import argparse
from datetime import datetime, date
from typing import Any, Dict, List

import requests


def _get_base() -> str:
    """
    Resolve de BASE / SERVICE_URL, con default al endpoint canónico.
    """
    base = os.getenv("BASE") or os.getenv("SERVICE_URL")
    if not base:
        base = "https://natacha-api-422255208682.us-central1.run.app"
    return base.rstrip("/")


def _short_hour(ts: str) -> str:
    """
    Recorta una ISO8601 a HH:MM (hora local/naive).
    """
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", ""))
        return dt.strftime("%H:%M")
    except Exception:
        return ts


def format_tareas(tareas: List[Dict[str, Any]]) -> str:
    if not tareas:
        return "  - (no hay tareas pendientes registradas para este proyecto)\n"

    lines: List[str] = []
    for t in tareas:
        title = t.get("title", "(sin título)")
        state = t.get("state", "")
        due = t.get("due") or ""
        if due:
            due_txt = f" — vence: {due}"
        else:
            due_txt = ""
        lines.append(f"  - [{state}] {title}{due_txt}")
    return "\n".join(lines) + "\n"


def format_eventos(eventos: List[Dict[str, Any]]) -> str:
    if not eventos:
        return "  - (no hay eventos registrados en el bundle v2)\n"

    lines: List[str] = []
    for e in eventos:
        summary = e.get("summary", "(sin título)")
        loc = e.get("location") or ""
        start = e.get("start") or ""
        end = e.get("end") or ""
        rango = ""
        if start or end:
            rango = f"{_short_hour(start)}–{_short_hour(end)}".strip("–")
        loc_txt = f" @ {loc}" if loc else ""
        if rango:
            lines.append(f"  - {rango}  {summary}{loc_txt}")
        else:
            lines.append(f"  - {summary}{loc_txt}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Daily starter v2 – Agenda ejecutiva del día con Natacha (engine de contexto v2)."
    )
    parser.add_argument(
        "--user",
        dest="user_id",
        default="sebastian",
        help="user_id (default: sebastian)",
    )
    parser.add_argument(
        "--project",
        dest="project",
        default="LLVC",
        help="Proyecto actual (default: LLVC)",
    )
    parser.add_argument(
        "--limit",
        dest="limit",
        type=int,
        default=10,
        help="Cantidad máxima de tareas a mostrar (default: 10)",
    )
    args = parser.parse_args()

    base = _get_base()
    url = f"{base}/memory/engine/context_bundle_v2"

    params: Dict[str, Any] = {
        "user_id": args.user_id,
        "project": args.project,
        "limit": args.limit,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Error llamando a context_bundle_v2:", repr(e), file=sys.stderr)
        print(f"URL: {url}", file=sys.stderr)
        print(f"Params: {params}", file=sys.stderr)
        sys.exit(1)

    summary = data.get("summary") or {}
    tasks_block = data.get("tasks") or {}
    events = data.get("events") or []

    headline = summary.get("headline") or "Sin headline en summary v2."
    pending_tasks: List[Dict[str, Any]] = tasks_block.get("pending") or []
    pending_top = pending_tasks[: args.limit]

    today = date.today().isoformat()

    print(f"=== Agenda ejecutiva Natacha — {today} ===")
    print()
    print("Prioridad absoluta del día:")
    print(f"  • {headline}")
    print()
    print("Tareas pendientes principales:")
    print(format_tareas(pending_top))
    print("Eventos relevantes:")
    print(format_eventos(events))
    print(f"(Fuente: /memory/engine/context_bundle_v2 — base={base})")


if __name__ == "__main__":
    main()
