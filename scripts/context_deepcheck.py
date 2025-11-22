#!/usr/bin/env python3
import os
import sys
import json
import argparse
import datetime as dt

import requests


def parse_args():
    p = argparse.ArgumentParser(
        description="Deep-check de contexto/memoria de Natacha para un user/proyecto."
    )
    p.add_argument("--user", "--user_id", dest="user_id", default="sebastian")
    p.add_argument("--project", dest="project", default="LLVC")
    p.add_argument("--recent_limit", type=int, default=20)
    p.add_argument("--json", action="store_true", help="Salida cruda en JSON")
    return p.parse_args()


def get_base():
    base = os.environ.get("BASE") or os.environ.get("SERVICE_URL")
    if not base:
        base = "http://localhost:8080"
    return base.rstrip("/")


def main():
    args = parse_args()
    base = get_base()
    user_id = args.user_id
    project = args.project
    recent_limit = args.recent_limit

    # Endpoint de engine de contexto
    url = f"{base}/memory/engine/context_bundle"
    params = {
        "user_id": user_id,
        "recent_limit": recent_limit,
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
    except Exception as e:
        print("❌ Error llamando a context_bundle:", repr(e))
        sys.exit(1)

    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code} desde {url}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()

    if args.json:
        print(json.dumps(
            {
                "base": base,
                "user_id": user_id,
                "project": project,
                "raw": data,
            },
            indent=2,
            ensure_ascii=False,
        ))
        return

    # ---- Interpretación amigable ----
    system_rule = data.get("system_rule")
    summary = data.get("summary")
    recent = data.get("recent") or data.get("recent_sample") or []
    semantic_status = data.get("semantic_v2_status") or data.get("semantic_status")

    print(f"Base: {base}")
    print(f"user_id: {user_id} | project (lógico): {project}")
    print("=" * 70)
    print("ENGINE DE CONTEXTO / MEMORIA")
    print("-" * 70)

    # System rule
    if system_rule:
        version = system_rule.get("version") or system_rule.get("id") or "desconocida"
        created_at = system_rule.get("created_at") or "?"
        print(f"System rule:         ✅ presente (versión: {version}, created_at: {created_at})")
    else:
        print("System rule:         ⚠️ NO presente en context_bundle")

    # Summary
    if summary:
        updated_at = summary.get("updated_at") or "?"
        text = summary.get("summary") or ""
        length = len(text)
        print(f"Summary:             ✅ presente (len={length} chars, updated_at={updated_at})")
    else:
        print("Summary:             ⚠️ NO presente")

    # Recent
    print()
    print(f"Recent / muestras recientes: {len(recent)} (limit={recent_limit})")
    if recent:
        # mostrar 3 ejemplos cortos
        for i, item in enumerate(recent[:3], start=1):
            kind = item.get("kind") or "?"
            created_at = item.get("created_at") or "?"
            note = item.get("note") or ""
            note_short = note.replace("\n", " ")
            if len(note_short) > 100:
                note_short = note_short[:97] + "..."
            print(f"  {i}) [{kind}] {created_at} → {note_short}")
    else:
        print("  ⚠️ No hay recent en el bundle.")

    # Semantic v2 status (si existe)
    print()
    if semantic_status:
        print(f"Semantic v2 status:  {semantic_status}")
    else:
        print("Semantic v2 status:  (no informado en esta respuesta)")

    print()
    print("Tip: para ver el JSON completo, podés correr con --json")


if __name__ == "__main__":
    main()
