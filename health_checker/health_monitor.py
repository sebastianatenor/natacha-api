import requests
from google.cloud import firestore
from datetime import datetime, UTC
import time

db = firestore.Client()

SERVICES = {
    "natacha-core": "http://localhost:8081/health",
}

def log_status(service, status, source="auto_check"):
    """Guarda el estado de un servicio en Firestore"""
    db.collection("system_health").add({
        "service": service,
        "status": status,
        "timestamp": datetime.now(UTC).isoformat(),
        "source": source
    })
    print(f"🗒️  {service}: {status}")

def check_services():
    """Chequea los servicios definidos en SERVICES"""
    for service, url in SERVICES.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                log_status(service, "✅ Core operativo y estable")
            else:
                log_status(service, f"⚠️ Respuesta inesperada ({response.status_code})")
        except Exception as e:
            log_status(service, f"❌ No responde — {e.__class__.__name__}")

def monitor_loop(interval=60):
    print(f"[{datetime.now(UTC).isoformat()}] 🩺 Iniciando monitoreo automático de salud...")
    while True:
        check_services()
        print(f"[{datetime.now(UTC).isoformat()}] 🔁 Próxima verificación en {interval}s")
        time.sleep(interval)

if __name__ == "__main__":
    monitor_loop(interval=60)
