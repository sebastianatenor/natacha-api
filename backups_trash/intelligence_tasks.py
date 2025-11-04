#!/usr/bin/env python3
"""
scripts/intelligence_tasks.py
Lee last_context.json y muestra las tareas pendientes por proyecto.
No llama a la API. Solo lectura local.
"""
from pathlib import Path
import json

ctx_path = Path("last_context.json")
if not ctx_path.exists():
    print("⚠️ No existe last_context.json. Corré antes:  python3 intelligence/startup.py")
    raise SystemExit(1)

data = json.loads(ctx_path.read_text())
inner = data.get("data") or data

projects = inner.get("projects") or []
duplicates = inner.get("duplicates") or []

print("== TAREAS PENDIENTES (desde last_context.json) ==")

if not projects:
    print("⚠️ No se encontraron proyectos en el contexto.")
else:
    for p in projects:
        name = p.get("name", "sin-nombre")
        pending = p.get("pending_tasks", 0)
        print(f"\n📁 {name} → {pending} pendiente(s)")
        # ojo: en /ops/insights no vienen todas las tareas expandidas,
        # así que mostramos lo que tenemos
        urgent = p.get("urgent_task")
        if urgent:
            print(f"   🔴 urgente: {urgent.get('title')}  (due: {urgent.get('due')})")

if duplicates:
    print("\n⚠️ Duplicados detectados:")
    for d in duplicates:
        print(f" - {d.get('title')} ({d.get('count')})")

print("\nListo ✅")
