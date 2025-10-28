import psutil, docker
from google.cloud import firestore
from datetime import datetime, UTC

def check_alerts():
    db = firestore.Client()
    alerts = []
    if psutil.cpu_percent() > 85:
        alerts.append("⚠️ CPU alta (>85%)")
    if psutil.virtual_memory().percent > 90:
        alerts.append("⚠️ Memoria saturada (>90%)")

    client = docker.from_env()
    for c in client.containers.list(all=True):
        if c.status != "running":
            alerts.append(f"❌ Contenedor detenido: {c.name}")

    if alerts:
        doc = {
            "service": "alerts-system",
            "alerts": alerts,
            "timestamp": datetime.now(UTC).isoformat()
        }
        db.collection("system_health").add(doc)
        print("🚨 ALERTA registrada en Firestore:", alerts)
    else:
        print("✅ Sin alertas detectadas.")
