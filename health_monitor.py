import os
import time
import requests
from google.cloud import firestore
from datetime import datetime
from subprocess import run

db = firestore.Client()
SERVICES = {
    "natacha-api": "http://natacha-api:8080/health",
    "natacha-core": "http://natacha-core:8080/health",
    "natacha-memory-console": "http://natacha-memory-console:8080/health"
}

def log_health(service, status, error=None):
    doc_ref = db.collection("system_health").document()
    doc_ref.set({
        "service": service,
        "status": status,
        "error": error or "",
        "timestamp": datetime.utcnow().isoformat()
    })

def check_services():
    for name, url in SERVICES.items():
        try:
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                print(f"✅ {name} OK")
                log_health(name, "✅")
            else:
                print(f"⚠️ {name} responde {res.status_code}")
                log_health(name, "❌", f"HTTP {res.status_code}")
                heal_service(name)
        except Exception as e:
            print(f"❌ {name} inalcanzable — {e}")
            log_health(name, "❌", str(e))
            heal_service(name)

def heal_service(name):
    print(f"🔧 Intentando autocuración de {name}...")
    try:
        run(["docker", "restart", name], check=False)
        time.sleep(5)
        print(f"✅ Reinicio de {name} ejecutado.")
        db.collection("auto_heal_logs").add({
            "service": name,
            "action": "restart",
            "timestamp": datetime.utcnow().isoformat(),
            "result": "success"
        })
    except Exception as e:
        db.collection("auto_heal_logs").add({
            "service": name,
            "action": "restart",
            "timestamp": datetime.utcnow().isoformat(),
            "result": "failed",
            "error": str(e)
        })
        print(f"🚨 Falló el intento de autocuración de {name}: {e}")

if __name__ == "__main__":
    print("[🩺] Iniciando Health Monitor — autocuración activa")
    while True:
        check_services()
        time.sleep(60)
