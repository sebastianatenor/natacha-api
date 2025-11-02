#!/usr/bin/env python3
import json
from pathlib import Path
import sys

CTX = Path("last_context.json")

print("== Natacha dedupe helper ==\n")

if not CTX.exists():
    print("⚠️ No existe last_context.json. Ejecutá primero:")
    print("   python3 intelligence/startup.py")
    sys.exit(1)

raw = json.loads(CTX.read_text(encoding="utf-8"))
data = raw.get("data") or {}
dups = data.get("duplicates") or []

if not dups:
    print("✅ No hay tareas duplicadas según /ops/insights.")
    sys.exit(0)

print(f"⚠️ Se detectaron {len(dups)} título(s) duplicado(s):\n")

for d in dups:
    title = d.get("title")
    count = d.get("count")
    ids = d.get("ids") or []
    print(f"- \"{title}\"  ({count} ocurrencias)")
    print("  IDs:")
    for i in ids:
        print(f"    • {i}")
    print("  👉 Para borrar una en la API (ejemplo):")
    print("     curl -X DELETE \"https://natacha-api-mkwskljrhq-uc.a.run.app/tasks/{ID}\"")
    print("     # reemplazar {ID} por uno de los de arriba")
    print()

print("Listo ✅ (no se borró nada, solo se mostraron los duplicados)\n")
