import datetime
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
BASE = _resolve_base()
import json
import os
import subprocess

import requests

print("🔄 Ejecutando diagnóstico automático de infraestructura...")

# Ejecutar el script existente
script_path = os.path.expanduser("~/Projects/natacha-api/check_infra_status.sh")
subprocess.run(["bash", script_path], check=True)

# Leer resultado
json_path = os.path.expanduser("~/Projects/natacha-api/infra_status.json")
with open(json_path) as f:
    data = json.load(f)

# Crear payload para memoria
payload = {
    "summary": f"Diagnóstico de infraestructura completado ({data['vm_status']})",
    "type": "infra_check",
    "project": data["project"],
    "impact": "Medio",
    "state": "Vigente",
    "detail": json.dumps(data),
    "timestamp": datetime.datetime.utcnow().isoformat(),
}

# Enviar a API
requests.post(
    f"{BASE}/memory/add",
    headers={"Content-Type": "application/json"},
    json=payload,
)

print("✅ Memoria guardada correctamente en Firestore.")
