#!/usr/bin/env python3
import requests
import json
import sys

BASE = "https://natacha-api-422255208682.us-central1.run.app"
USER = "sebastian"
PROJ = "LLVC"

print("== TAREAS: deep-diagnosis v2 (filtrando en cliente) ==")

# Usamos /tasks/list SIN filtros porque la variante con user+project tira 500
url = f"{BASE}/tasks/list?limit=200"
print(f"Llamando a: {url}")

try:
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        print(f"HTTP {r.status_code}: {r.text}")
        sys.exit(1)

    data = r.json()
    items = data.get("items", [])
    print(f"Total tareas en API (todas): {len(items)}")

    # Filtro local por user_id y project
    filtered = [
        t for t in items
        if t.get("user_id") == USER and t.get("project") == PROJ
    ]
    print(f"Tareas filtradas para user={USER}, project={PROJ}: {len(filtered)}")

    broken = []

    for t in filtered:
        required = ["id", "title", "state", "created_at", "user_id", "project"]
        missing = [k for k in required if k not in t]
        if missing:
            broken.append({
                "id": t.get("id"),
                "title": t.get("title"),
                "missing": missing,
                "raw": t,
            })

    print("\n== TAREAS CON CAMPOS FALTANTES (solo LLVC) ==")
    print(json.dumps(broken, indent=2, ensure_ascii=False))

    if not broken:
        print("\n✅ No se detectaron campos faltantes en las tareas de LLVC.")

except Exception as e:
    print("EXCEPTION:", repr(e))
    sys.exit(1)
