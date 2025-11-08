#!/usr/bin/env python3
import os
import json
import sys
from pathlib import Path
# == Canonical resolver (no hardcodes) ==
import os
from pathlib import Path

def _resolve_base() -> str:
    # 1) env
    v = os.getenv("NATACHA_CONTEXT_API") or os.getenv("CANON")
    if v: return v
    # 2) REGISTRY.md
    reg = os.path.expanduser("~/REGISTRY.md")
    try:
        with open(reg, "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("- URL producción:"):
                    return line.split(":",1)[1].strip()
    except Exception:
        pass
    # 3) vacío: que el caller falle visiblemente si intenta usarlo
    return ""
BASE = _resolve_base()
# == end resolver ==

# Base de la API: primero NATACHA_CONTEXT_API, si no existe usa CANON (exportada en tu shell),
# y como último fallback deja la URL LIVE conocida.
BASE = os.getenv(
    "NATACHA_CONTEXT_API",
    os.environ.get("CANON","")
)

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
    print(f'- "{title}"  ({count} ocurrencias)')
    print("  IDs:")
    for i in ids:
        print(f"    • {i}")
    print("  👉 Para borrar una en la API (ejemplo):")
    print(f'     curl -X DELETE "{BASE}/tasks/{{ID}}"')
    print("     # reemplazar {ID} por uno de los de arriba")
    print()

print("Listo ✅ (no se borró nada, solo se mostraron los duplicados)\n")
