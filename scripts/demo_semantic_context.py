#!/usr/bin/env python3
import os
import json
import sys
import pathlib

# Aseguramos que Python vea la raíz del repo (natacha-api) para importar natacha_core
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from natacha_core import memory_bridge


def main():
    # Parámetros por defecto (se pueden overridear con variables de entorno)
    user = os.getenv("NATACHA_USER_ID", "sebastian")
    project = os.getenv("NATACHA_PROJECT", "LLVC")
    query = os.getenv("NATACHA_QUERY", "proformas")

    print("== PARAMETROS ==")
    print(f"user: {user} | project: {project} | query: {query}")
    print()

    # Llamamos al motor de contexto (ya integrado con semantic_v2)
    ctx = memory_bridge.retrieve_context(
        limit=5,
        user=user,
        semantic_project=project,
        semantic_q=query,
        semantic_limit=5,
    )

    # --- 1) System rule (core-v1) ---
    system_rule = ctx.get("system_rule") or {}
    print("== SYSTEM RULE (core-v1) ==")
    if system_rule:
        print(json.dumps(system_rule, ensure_ascii=False, indent=2))
    else:
        print("(sin system_rule)")
    print()

    # --- 2) Summary v1 (consolidado clásico) ---
    legacy_summary_doc = ctx.get("summary") or {}
    legacy_summary_text = None
    if isinstance(legacy_summary_doc, dict):
        legacy_summary_text = legacy_summary_doc.get("summary")

    print("== SUMMARY v1 (consolidado) ==")
    if legacy_summary_text:
        print(legacy_summary_text)
    else:
        print("(sin summary v1 para este user)")
    print()

    # --- 3) Bloque semántico v2 (lo que acabamos de integrar) ---
    semantic_block = (ctx.get("semantic_v2") or {}).get("result") or {}
    semantic_summary = semantic_block.get("summary")
    semantic_items = semantic_block.get("items") or []

    print("== SUMMARY SEMANTICO v2 (focalizado) ==")
    if semantic_summary:
        print(semantic_summary)
    else:
        print("(sin summary semántico para esta query)")
    print()

    print("== TOP SEMANTIC ITEMS ==")
    if semantic_items:
        for item in semantic_items[:5]:
            text = item.get("text", "")
            tags = item.get("tags", [])
            score = item.get("score", 0.0)
            print(f"- {text} | tags={tags} | score={score}")
    else:
        print("(no hay ítems semánticos)")
    print()

    # --- 4) PROPOSED CONTEXT BLOCK: lo que el cerebro de Natacha podría usar ---
    context_parts = []

    # a) Nota de sistema si existe
    note = None
    if isinstance(system_rule, dict):
        note = system_rule.get("note")
    if note:
        context_parts.append(f"SYSTEM RULE (core-v1):\n{note}")

    # b) Summary v1 clásico
    if legacy_summary_text:
        context_parts.append(f"Resumen ejecutivo v1:\n{legacy_summary_text}")

    # c) Summary semántico focalizado
    if semantic_summary:
        context_parts.append(f"Memoria semántica focalizada:\n{semantic_summary}")

    full_context_block = "\n\n---\n\n".join(context_parts) if context_parts else "(sin contexto compuesto)"

    print("== CONTEXT BLOCK PROPUESTO PARA PROMPT ==")
    print(full_context_block)
    print()

    print("== DEBUG: ORIGEN COMPLETO (keys de ctx) ==")
    print(sorted(list(ctx.keys())))


if __name__ == "__main__":
    main()
