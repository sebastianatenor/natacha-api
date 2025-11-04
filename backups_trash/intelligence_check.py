#!/usr/bin/env python3
import json
from pathlib import Path

ctx_path = Path("last_context.json")
boot_path = Path("logs/boot_history.jsonl")

print("== Natacha intelligence check ==\n")

# 1) último contexto
if ctx_path.exists():
    data = json.loads(ctx_path.read_text(encoding="utf-8"))
    source = data.get("source")
    print(f"📦 last_context.json OK (source: {source})")
    # ver proyectos
    projects = []
    if isinstance(data.get("data"), dict):
        projects = data["data"].get("projects") or []
    if projects:
        print("  Proyectos detectados:")
        for p in projects:
            print(f"   - {p.get('name')} (pending: {p.get('pending_tasks')})")
    # mostrar duplicados si hay
    dups = []
    if isinstance(data.get("data"), dict):
        dups = data["data"].get("duplicates") or []
    if dups:
        print("\n  ⚠️ Tareas duplicadas detectadas:")
        for d in dups:
            print(f"   - {d['title']} ({d['count']})")
else:
    print("⚠️ No existe last_context.json. Ejecutá:  python3 intelligence/startup.py")

print("\n-- boot history --")
if boot_path.exists():
    lines = boot_path.read_text(encoding="utf-8").strip().splitlines()
    print(f"  Entradas: {len(lines)}")
    for line in lines[-5:]:
        try:
            obj = json.loads(line)
            print(f"   • {obj.get('loaded_at')} ← {obj.get('source')}")
        except Exception:
            print(f"   • {line[:80]} ...")
else:
    print("  (no hay logs/boot_history.jsonl)")

print("\nListo ✅")
