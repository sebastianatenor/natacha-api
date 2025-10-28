from google.cloud import firestore
from datetime import datetime
from subprocess import run
import time

db = firestore.Client()

def restart_service(service):
    print(f"🔁 Reiniciando {service}...")
    try:
        run(["docker", "restart", service], check=True)
        db.collection("auto_heal_logs").add({
            "service": service,
            "action": "restart",
            "timestamp": datetime.utcnow().isoformat(),
            "result": "ok"
        })
        print(f"✅ {service} reiniciado correctamente.")
    except Exception as e:
        db.collection("auto_heal_logs").add({
            "service": service,
            "action": "restart",
            "timestamp": datetime.utcnow().isoformat(),
            "result": "error",
            "error": str(e)
        })
        print(f"❌ Error al reiniciar {service}: {e}")

if __name__ == "__main__":
    restart_service("natacha-core")
    time.sleep(3)
