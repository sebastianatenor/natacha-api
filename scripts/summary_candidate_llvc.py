#!/usr/bin/env python3
"""
summary_candidate_llvc.py

Genera un resumen ejecutivo "candidato" para LLVC usando:
- summary v1 actual desde /memory/engine/context_bundle
- summary semántico v2 (si existe en semantic_v2.summary)
- últimas notas recientes (recent / recent_sample)

Uso:
  BASE="https://natacha-api-422255208682.us-central1.run.app" \
    python3 scripts/summary_candidate_llvc.py --user sebastian --project LLVC

Opcional:
  --json  -> devuelve salida estructurada en JSON
"""

import os
import sys
import json
import argparse
from typing import Any, Dict, List, Optional

import requests


def get_base() -> str:
    base = os.getenv("BASE") or os.getenv("SERVICE_URL") or "http://localhost:8080"
    return base.rstrip("/")


def fetch_context_bundle(base: str, user_id: str, recent_limit: int = 20) -> Dict[str, Any]:
    url = f"{base}/memory/engine/context_bundle"
    params = {
        "user_id": user_id,
        "recent_limit": str(recent_limit),
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


def safe_get_recent(bundle: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Devuelve una lista de items recientes a partir de:
    - bundle["recent"]
    - bundle["recent_sample"]
    Maneja casos raros donde venga como dict u otro tipo.
    """
    recent = bundle.get("recent") or bundle.get("recent_sample") or []

    # Si viene como dict, tratamos de sacar 'items' o lo convertimos a lista vacía
    if isinstance(recent, dict):
        recent = recent.get("items") or []

    if not isinstance(recent, list):
        return []

    clean: List[Dict[str, Any]] = []
    for item in recent:
        if not isinstance(item, dict):
            continue
        note = (item.get("note") or "").strip()
        if not note:
            continue
        clean.append(item)
    return clean


def build_candidate(
    summary_v1: str,
    semantic_summary: str,
    recent_items: List[Dict[str, Any]],
    project: Optional[str] = None,
) -> str:
    """
    Construye un bloque de texto candidato para summary v1.
    Mezcla:
      - summary v1 actual (si existe)
      - resumen semántico v2
      - últimas notas recientes (hasta 5)
    """
    lines: List[str] = []

    header_project = f" — {project}" if project else ""
    lines.append(f"Brief ejecutivo LLVC{header_project} — candidato a summary v1")
    lines.append("")

    # Capa 1: summary v1 actual
    if summary_v1:
        lines.append("=== Capa 1 — Summary v1 actual ===")
        lines.append(summary_v1.strip())
        lines.append("")

    # Capa 2: memoria semántica v2
    if semantic_summary:
        lines.append("=== Capa 2 — Memoria semántica v2 (foco operativo) ===")
        lines.append(semantic_summary.strip())
        lines.append("")

    # Capa 3: últimas notas recientes
    if recent_items:
        lines.append("=== Capa 3 — Últimas notas recientes relevantes ===")
        for item in recent_items[:5]:
            created_at = item.get("created_at") or "?"
            kind = item.get("kind") or "?"
            note = (item.get("note") or "").strip().replace("\n", " ")
            if len(note) > 160:
                note = note[:157] + "..."
            lines.append(f"- [{kind}] {created_at} → {note}")
        lines.append("")

    if not (summary_v1 or semantic_summary or recent_items):
        lines.append("(No hay datos suficientes para construir un summary candidato.)")

    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="Generar resumen ejecutivo candidato para LLVC.")
    parser.add_argument("--user", "--user_id", dest="user_id", required=True, help="user_id (ej: sebastian)")
    parser.add_argument("--project", dest="project", default="LLVC", help="Proyecto lógico (meta)")
    parser.add_argument("--recent_limit", type=int, default=20, help="Límite de memorias recientes a considerar")
    parser.add_argument("--json", action="store_true", help="Salida en JSON estructurado")
    args = parser.parse_args()

    base = get_base()
    user_id = args.user_id
    project = args.project

    print(f"Base: {base}")
    print(f"user_id: {user_id} | project: {project}")
    print("== Generando resumen ejecutivo candidato ==\n")

    try:
        bundle = fetch_context_bundle(base, user_id, args.recent_limit)
    except Exception as e:
        print(f"ERROR al llamar a context_bundle: {e}", file=sys.stderr)
        sys.exit(1)

    # Extraer summary v1
    summary_block = bundle.get("summary") or {}
    summary_v1 = (summary_block.get("summary") or "").strip() if isinstance(summary_block, dict) else ""

    # Extraer summary semántico v2 (si existe)
    semantic_block = bundle.get("semantic_v2") or {}
    semantic_summary = ""
    if isinstance(semantic_block, dict):
        semantic_summary = (semantic_block.get("summary") or "").strip()

    # Extraer recent
    recent_items = safe_get_recent(bundle)

    candidate_text = build_candidate(summary_v1, semantic_summary, recent_items, project=project)

    if args.json:
        out = {
            "base": base,
            "user_id": user_id,
            "project": project,
            "summary_v1": summary_v1,
            "semantic_summary": semantic_summary,
            "recent_items_count": len(recent_items),
            "candidate": candidate_text,
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(candidate_text)


if __name__ == "__main__":
    main()
