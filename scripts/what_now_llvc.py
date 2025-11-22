#!/usr/bin/env python3
import os
import json
import argparse
import subprocess
import sys
from datetime import datetime

def run_tasks_urgency(user_id: str, project: str) -> dict:
    """
    Llama a scripts/tasks_urgency.py --json y devuelve el JSON parseado.
    Así reutilizamos exactamente la misma lógica que ya sabemos que funciona.
    """
    cmd = [
        sys.executable,
        "scripts/tasks_urgency.py",
        "--user", user_id,
        "--project", project,
        "--json",
    ]
    try:
        output = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR ejecutando tasks_urgency.py: {e}", file=sys.stderr)
        print(e.output, file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(output)
    except json.JSONDecodeError as e:
        print("ERROR: la salida de tasks_urgency.py no es JSON válido.", file=sys.stderr)
        print(output, file=sys.stderr)
        sys.exit(1)

    return data


def human_due(due: str | None) -> str:
    if not due:
        return "-"
    # due puede venir como "2025-11-30" o "2025-12-01T12:00:00"
    return due


def main():
    parser = argparse.ArgumentParser(
        description="Resumen ejecutivo: ¿qué hago ahora con LLVC?"
    )
    parser.add_argument("--user", required=True, help="user_id (ej: sebastian)")
    parser.add_argument("--project", required=True, help="project (ej: LLVC)")
    parser.add_argument(
        "--top",
        type=int,
        default=3,
        help="Cantidad de tareas prioritarias a mostrar (default: 3)",
    )
    args = parser.parse_args()

    data = run_tasks_urgency(args.user, args.project)
    items = data.get("items", [])

    # Filtrar solo pendientes
    pending = [t for t in items if t.get("state") == "pending"]

    # Ordenar por urgency_score desc (si no está, asumir 0)
    pending.sort(key=lambda t: t.get("urgency_score", 0), reverse=True)

    top_n = pending[: args.top]

    print(f"Qué es lo más importante para {args.project} ahora mismo:\n")

    if not top_n:
        print("No hay tareas pendientes para este proyecto. 🎉")
        sys.exit(0)

    for idx, t in enumerate(top_n, start=1):
        urgency = t.get("urgency", "DESCONOCIDA")
        score = t.get("urgency_score", 0)
        title = t.get("title") or "(sin título)"
        detail = t.get("detail") or ""
        due = human_due(t.get("due"))
        tid = t.get("id")

        print(f"{idx}) [{urgency}] {title}")
        print(f"   - Score: {score} | Due: {due} | id: {tid}")
        if detail:
            print(f"   - Detalle: {detail}")
        print()

    # Bonus: si querés, podríamos imprimir un mini-resumen tipo “acción 1, 2, 3”
    print("Sugerencia de foco inmediato:")
    for idx, t in enumerate(top_n, start=1):
        title = t.get("title") or "(sin título)"
        print(f" - {idx}) {title}")


if __name__ == "__main__":
    main()
