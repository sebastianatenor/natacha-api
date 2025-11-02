import subprocess
import json
import requests
import datetime
import os

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
    "https://natacha-api-422255208682.us-central1.run.app/memory/add",
    headers={"Content-Type": "application/json"},
    json=payload
)

print("✅ Memoria guardada correctamente en Firestore.")
