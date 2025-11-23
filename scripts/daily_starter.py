import os
import sys
import argparse
from datetime import datetime, date
from typing import Any, Dict, List

import requests

SERVICE_URL = os.getenv(
    "SERVICE_URL",
    "https://natacha-api-422255208682.us-central1.run.app",
)


def _safe_get(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e), "url": url, "params": params}


def format_tareas(tareas: List[Dict[str, Any]]) -> str:
    if not tareas:
        return "  - (no hay tareas registradas para este proyecto)\n"

    lines = []
    for t in tareas:
        title = t.get("title", "(sin título)")
        state = t.get("state", "")
        due = t.get("due") or ""
        due_txt = f" — vence: {due}" if due else ""
        lines.append(f"  - [{state}] {title}{due_txt}")
    return "\n".join(lines) + "\n"


def _short_hour(ts: str) -> str:
    # ts viene como ISO8601, lo mostramos HH:MM (UTC)
    try:
        dt = datetime.fromisoformat(ts.replace("Z", ""))
        return dt.strftime("%H:%M")
    except Exception:
        return ts


def format_eventos(eventos: List[Dict[str, Any]]) -> str:
    if not eventos:
        return "  - (no hay eventos en el calendario demo)\n"

    lines = []
    for e in eventos:
        summary = e.get("summary", "(sin título)")
        loc = e.get("location") or ""
        start = e.get("start") or ""
        end = e.get("end") or ""
        rango = f"{_short_hour(start)}–{_short_hour(end)}" if start and end else ""
        loc_txt = f" @ {loc}" if loc else ""
        lines.append(f"  - {rango}  {summary}{loc_txt}")
    return "\n".join(lines) + "\n"


def shorten_estado_general(text: str) -> str:
    """
    Recorta el bloque de summary para que el DAILY STARTER muestre
    sólo el contexto más accionable y no todo el brief estratégico.
    """
    if not text:
        return "(sin summary)"

    # Separar en líneas y sacar vacías
    lines = [l for l in text.splitlines() if l.strip()]

    trimmed: List[str] = []
    for line in lines:
        # Cortamos si empieza el Brief o el marcador [...]
        if line.startswith("Brief Ejecutivo"):
            break
        if line.strip() == "[...]":
            break

        trimmed.append(line)

        # Límite de seguridad por si no aparece "Brief Ejecutivo"
        if len(trimmed) >= 8:
            break

    return "\n".join(trimmed) if trimmed else text


def main():
    parser = argparse.ArgumentParser(
        description="Daily starter pack – Agenda ejecutiva del día con Natacha."
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
        "--hours-ahead",
        dest="hours_ahead",
        type=int,
        default=12,
        help="Ventana de horas hacia adelante para eventos (default: 12)",
    )
    args = parser.parse_args()

    params = {
        "user_id": args.user_id,
        "project": args.project,
        "hours_ahead": args.hours_ahead,
    }

    agenda = _safe_get(f"{SERVICE_URL}/natacha/agenda_hoy", params=params)

    if agenda.get("status") != "ok":
        print("❌ Error al obtener agenda_hoy")
        print(agenda)
        sys.exit(1)


    hoy = date.today().strftime("%Y-%m-%d")
    print("================================================================================")
    print(f"📅 DAILY STARTER PACK – {hoy} | user: {args.user_id} | project: {args.project}")
    print("================================================================================")
    print()

    # BLOQUE 1 – Estado general (recortado)
    raw_estado_general = agenda.get("estado_general") or "(sin summary)"
    estado_general = shorten_estado_general(raw_estado_general)

    print("🧠 ESTADO GENERAL")
    print("─────────────────")
    print(estado_general)
    print()

    # BLOQUE 2 – Puntos clave
    puntos = agenda.get("puntos_clave") or []
    print("⭐ PUNTOS CLAVE")
    print("───────────────")
    if not puntos:
        print("  - (sin puntos clave cargados)")
    else:
        for p in puntos:
            # cada item ya viene como texto largo; lo mostramos como bullet
            print(f"  - {p}")
    print()

    # BLOQUE 3 – Tareas relevantes
    tareas = agenda.get("tareas_relevantes") or []
    print("📋 TAREAS RELEVANTES")
    print("─────────────────────")
    print(format_tareas(tareas))

    # BLOQUE 4 – Eventos de hoy
    eventos = agenda.get("eventos_hoy") or []
    print("📆 AGENDA DE HOY (Calendar demo)")
    print("────────────────────────────────")
    print(format_eventos(eventos))

    # BLOQUE 5 – Recomendación del día
    recomendacion = agenda.get("recomendacion_del_dia") or "(sin recomendación)"
    print("🎯 RECOMENDACIÓN DEL DÍA")
    print("────────────────────────")
    print(f"  → {recomendacion}")
    print()

    gen_at = agenda.get("generated_at", "")
    if gen_at:
        print(f"(Generado por /natacha/agenda_hoy en: {gen_at})")


if __name__ == "__main__":
    main()
