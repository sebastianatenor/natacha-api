#!/usr/bin/env python3
"""
memory_integrity.py

Chequeo de integridad de memoria de Natacha para un user_id/proyecto.

- Llama a /memory/engine/context_bundle
- Verifica:
  * system_rule presente y con texto
  * summary presente y con texto
  * "edad" del summary (fresh / ok / stale / very_stale)
  * cantidad de memorias recientes
  * posibles notas duplicadas en recent (mismo texto varias veces)

Uso:
  BASE="https://natacha-api-422255208682.us-central1.run.app" \
    python3 scripts/memory_integrity.py --user sebastian --project LLVC

Opcional:
  --json  -> devuelve salida estructurada en JSON
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

import requests


def iso_to_dt(value: str):
    """Convierte ISO 8601 a datetime o devuelve None si falla."""
    if not value:
        return None
    try:
        # Aceptar timestamps con Z o con +00:00
        value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except Exception:
        return None


def build_report(bundle: dict, user_id: str, project: str | None, base: str) -> dict:
    # system_rule
    system_rule = bundle.get("system_rule") or bundle.get("system") or {}
    sys_rule_text = (system_rule.get("rule") or "").strip()
    sys_rule_version = system_rule.get("version") or "unknown"
    ok_system_rule = bool(sys_rule_text)

    # summary
    summary = bundle.get("summary") or {}
    summary_text = (summary.get("summary") or "").strip()
    ok_summary = bool(summary_text)

    updated_raw = summary.get("updated_at")
    updated_dt = iso_to_dt(updated_raw)
    summary_age_days: int | None = None
    summary_freshness = "unknown"

    if updated_dt is not None:
        # Normalizar: si viene sin tz, asumimos UTC
        if updated_dt.tzinfo is None:
            updated_dt = updated_dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = now - updated_dt
        summary_age_days = delta.days

        if summary_age_days <= 1:
            summary_freshness = "fresh"
        elif summary_age_days <= 3:
            summary_freshness = "ok"
        elif summary_age_days <= 7:
            summary_freshness = "stale"
        else:
            summary_freshness = "very_stale"

    # recent (puede venir como recent o recent_sample)
    recent = bundle.get("recent") or bundle.get("recent_sample") or []
    recent_count = len(recent)

    # Duplicados por nota en recent
    duplicates = []
    by_note: dict[str, list[dict]] = {}

    for item in recent:
        # item puede ser:
        # - dict con campos {note, summary, raw: {note}}  ✅
        # - string suelto (texto)                         ✅
        if isinstance(item, dict):
            raw_note = item.get("note") or item.get("summary")
            raw = item.get("raw")
            if not raw_note and isinstance(raw, dict):
                raw_note = raw.get("note") or raw.get("summary")
        else:
            raw_note = str(item)

        note = (raw_note or "").strip()
        if not note:
            continue

        by_note.setdefault(note, []).append(item)

    for note, items in by_note.items():
        if len(items) > 1:
            duplicates.append(
                {
                    "note": note,
                    "count": len(items),
                    "ids": [
                        x.get("id") for x in items
                        if isinstance(x, dict) and x.get("id")
                    ],
                    "created_at": [
                        x.get("created_at") for x in items
                        if isinstance(x, dict) and x.get("created_at")
                    ],
                }
            )

    warnings: list[str] = []

    if not ok_system_rule:
        warnings.append("system_rule_missing")

    if not ok_summary:
        warnings.append("summary_missing")

    if summary_freshness in ("stale", "very_stale"):
        warnings.append(f"summary_{summary_freshness}")

    if duplicates:
        warnings.append("recent_duplicates")

    status = "ok" if not warnings else "warnings"

    return {
        "status": status,
        "warnings": warnings,
        "meta": {
            "base": base,
            "user_id": user_id,
            "project": project,
        },
        "system_rule": {
            "present": ok_system_rule,
            "version": sys_rule_version,
            "rule_preview": sys_rule_text[:120],
        },
        "summary": {
            "present": ok_summary,
            "age_days": summary_age_days,
            "freshness": summary_freshness,
            "updated_at": updated_raw,
            "preview": summary_text[:200],
        },
        "recent": {
            "count": recent_count,
            "duplicates": duplicates,
        },
    }


def print_human(report: dict) -> None:
    base = report["meta"]["base"]
    user_id = report["meta"]["user_id"]
    project = report["meta"]["project"]

    status = report["status"]
    warnings = report["warnings"]

    icon_status = "✅" if status == "ok" else "⚠️"

    print("== MEMORY INTEGRITY — Natacha ==")
    print(f"Base: {base}")
    print(f"user_id: {user_id} | project: {project}")
    print("Estado general:", icon_status, status.upper())
    if warnings:
        print("Warnings:", ", ".join(warnings))
    else:
        print("Warnings: ninguno")

    print("\n-- System Rule --")
    sr = report["system_rule"]
    print("  Presente: ", "✅" if sr["present"] else "❌")
    print("  Versión:  ", sr["version"])
    if sr["rule_preview"]:
        print("  Preview:  ", sr["rule_preview"])

    print("\n-- Summary --")
    s = report["summary"]
    print("  Presente:   ", "✅" if s["present"] else "❌")
    print(
        "  Freshness:  ",
        s["freshness"],
        f"({s['age_days']} días)" if s["age_days"] is not None else "",
    )
    print("  updated_at: ", s["updated_at"] or "-")
    if s["preview"]:
        print("  Preview:    ", s["preview"])

    print("\n-- Recent --")
    r = report["recent"]
    print("  Cantidad de memorias recientes:", r["count"])
    if r["duplicates"]:
        print("  Posibles duplicados por nota:")
        for dup in r["duplicates"]:
            print("   - Nota:", dup["note"])
            print("     count:", dup["count"])
            print("     ids:", ", ".join(dup["ids"]) if dup["ids"] else "-")
    else:
        print("  No se detectaron notas duplicadas en recent.")

    print("\nResumen ejecutivo:")
    if "system_rule_missing" in warnings:
        print(" - ⚠️ Falta system_rule: revisar configuración del motor de contexto.")
    if "summary_missing" in warnings:
        print(" - ⚠️ Falta summary: generar / refrescar resumen global del usuario.")
    if "summary_stale" in warnings:
        print(" - ⚠️ Summary algo viejo: recomendable refrescar en los próximos días.")
    if "summary_very_stale" in warnings:
        print(" - 🔴 Summary muy viejo: conviene regenerarlo cuanto antes.")
    if "recent_duplicates" in warnings:
        print(
            " - ⚠️ Hay notas repetidas en recent: probable que el mismo tema esté apareciendo muchas veces."
        )
    if not warnings:
        print(" - 🟢 Memoria consistente y sin señales de alarma.")


def main():
    parser = argparse.ArgumentParser(
        description="Chequeo de integridad de memoria de Natacha."
    )
    parser.add_argument(
        "--user",
        "--user_id",
        dest="user_id",
        required=True,
        help="user_id a inspeccionar (ej: sebastian)",
    )
    parser.add_argument(
        "--project",
        dest="project",
        default=None,
        help="Proyecto (solo para meta, ej: LLVC)",
    )
    parser.add_argument(
        "--json", action="store_true", help="Salida en JSON en lugar de texto humano"
    )
    args = parser.parse_args()

    base = os.getenv(
        "BASE", "https://natacha-api-422255208682.us-central1.run.app"
    ).rstrip("/")

    url = f"{base}/memory/engine/context_bundle"
    params = {
        "user_id": args.user_id,
        "recent_limit": "50",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR al llamar a {url}: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        bundle = resp.json()
    except Exception as e:
        print("ERROR: la respuesta no es JSON válido:", e, file=sys.stderr)
        print("Cuerpo:", resp.text[:500], file=sys.stderr)
        sys.exit(1)

    report = build_report(bundle, args.user_id, args.project, base)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human(report)


if __name__ == "__main__":
    main()
