#!/usr/bin/env python3
"""
Lee last_context.json y muestra:
- tareas con due (ordenadas)
- tareas que vencen en las próximas 48 hs
- tareas sin fecha (según alerts del /ops/insights)
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

CTX_FILE = Path("last_context.json")


def load_context():
    if not CTX_FILE.exists():
        print(
            "⚠️ No existe last_context.json. Corré primero: python3 intelligence/startup.py"
        )
        return None
    return json.loads(CTX_FILE.read_text(encoding="utf-8"))


def parse_iso(dt_str):
    if not dt_str:
        return None
    try:
        # admite ...Z
        if dt_str.endswith("Z"):
            return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return datetime.fromisoformat(dt_str)
    except Exception:
        return None


def main():
    data = load_context()
    if not data:
        return

    # la data puede venir como data["projects"] o data["data"]["projects"]
    projects = data.get("projects") or (data.get("data") or {}).get("projects") or []
    if not projects:
        print("⚠️ El contexto no trae 'projects'. Nada para mostrar.")
        return

    now = datetime.now(timezone.utc)
    soon = now + timedelta(hours=48)

    print("== TAREAS CON FECHA (desde last_context.json) ==")

    tasks_with_due = []
    tasks_without_due = []

    for proj in projects:
        name = proj.get("name", "sin-nombre")
        # en /ops/insights las tareas vienen dentro del proyecto como pending_tasks? no: viene 'pending_tasks' (número) y opcionalmente 'alerts'
        # pero nosotros también tenemos los duplicados en data["data"]["duplicates"]
        # así que acá vamos a usar solo lo que sabemos seguro: las urgentes
        urgent = proj.get("urgent_task")
        alerts = proj.get("alerts") or []

        if urgent:
            due_str = urgent.get("due")
            due_dt = parse_iso(due_str)
            tasks_with_due.append((name, urgent, due_dt))

        # detectar "tareas sin fecha" desde alerts
        no_due_alerts = [a for a in alerts if "sin fecha" in a.lower()]
        if no_due_alerts:
            tasks_without_due.append((name, no_due_alerts))

    # ordenar por fecha las que sí tienen due
    tasks_with_due = [t for t in tasks_with_due if t[2] is not None]
    tasks_with_due.sort(key=lambda x: x[2])

    if tasks_with_due:
        for name, task, due_dt in tasks_with_due:
            due_iso = due_dt.isoformat()
            title = task.get("title", "(sin título)")
            mark = "🟡"
            if now <= due_dt <= soon:
                mark = "🔴"
            print(f"- {mark} {title}  | proyecto: {name} | vence: {due_iso}")
    else:
        print("ℹ️ No se detectaron tareas con fecha en el contexto.")

    print("\n== TAREAS/PROYECTOS SIN FECHA DETECTADA ==")
    if tasks_without_due:
        for name, alerts in tasks_without_due:
            print(f"- {name}: " + " / ".join(alerts))
    else:
        print("ℹ️ No había alerts de tareas sin fecha.")

    # duplicados (opcional)
    duplicates = (
        (data.get("data") or {}).get("duplicates") or data.get("duplicates") or []
    )
    if duplicates:
        print("\n== DUPLICADOS DETECTADOS ==")
        for d in duplicates:
            print(f"- {d.get('title')} ({d.get('count')})")
    print("Listo ✅")


if __name__ == "__main__":
    main()
