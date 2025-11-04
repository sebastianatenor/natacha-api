#!/usr/bin/env python3
"""
scripts/intelligence_summary.py
Resumen rápido de inteligencia: contexto, proyectos, duplicados y arranques.
"""

import json
import subprocess
from pathlib import Path

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()

# 1) Preflight check
subprocess.run(["./scripts/preflight_check.sh"], check=True)

# 2) Registry check
subprocess.run(["python3", "scripts/registry_check.py"], check=True)

# 3) Cargar contexto
ctx_file = Path("last_context.json")
if not ctx_file.exists():
    print("⚠️  No existe last_context.json")
    exit(1)

data = json.loads(ctx_file.read_text())

ctx = data.get("data", data)
projects = ctx.get("projects", [])
duplicates = ctx.get("duplicates", [])
raw = ctx.get("raw", {})

print("\n== Resumen de inteligencia ==\n")

if not projects:
    print("⚠️  No se detectaron proyectos en el contexto.")
else:
    print(f"🧩 {len(projects)} proyecto(s) detectado(s):")
    for p in projects:
        print(f" - {p.get('name')} → {p.get('pending_tasks')} tareas pendientes")

if duplicates:
    print("\n⚠️  Tareas duplicadas detectadas:")
    for d in duplicates:
        print(f" - {d['title']} ({d['count']})")

if raw:
    print(f"\n📊 Registros brutos: {raw}")

# 4) Mostrar historial de arranques
log_file = Path("logs/boot_history.jsonl")
if log_file.exists():
    print("\n== Historial de arranques ==\n")
    lines = log_file.read_text().splitlines()[-5:]
    for l in lines:
        e = json.loads(l)
        print(f" - {e['loaded_at']} ← {e['source']}  (projects: {e.get('projects')})")
else:
    print("\nℹ️  No hay boot_history.jsonl todavía.")

print("\nListo ✅")
