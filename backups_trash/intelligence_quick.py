#!/usr/bin/env python3
"""
scripts/intelligence_quick.py
Chequeo rápido de lo que Natacha cargó en el último arranque.
NO llama a Cloud Run, solo lee last_context.json y el boot_history.
"""
from pathlib import Path
import json

ctx_path = Path("last_context.json")
if not ctx_path.exists():
    print("⚠️ No existe last_context.json. Corré antes:  python3 intelligence/startup.py")
    raise SystemExit(1)

data = json.loads(ctx_path.read_text())

source = data.get("source")
inner = data.get("data") or data  # por si en algún momento cambia la forma
projects = inner.get("projects") or []
duplicates = inner.get("duplicates") or []
raw = inner.get("raw") or {}

print("== Natacha intelligence quick ==")
print(f"• Fuente: {source}")
print(f"• Proyectos vistos: {len(projects)}")
for p in projects:
    print(f"   - {p.get('name')} → {p.get('pending_tasks')} pendientes")

if duplicates:
    print("• Duplicados 👇")
    for d in duplicates:
        print(f"   - {d.get('title')} ({d.get('count')})")
else:
    print("• Duplicados: ninguno ✅")

if raw:
    print(f"• Raw: {raw}")

# boot history
log_path = Path("logs/boot_history.jsonl")
if log_path.exists():
    lines = log_path.read_text().splitlines()
    last = lines[-1]
    j = json.loads(last)
    print("• Último boot:", j["loaded_at"], "←", j["source"])
else:
    print("• boot_history.jsonl: no existe todavía")

print("Listo ✅")
