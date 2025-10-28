import requests
import time
from datetime import datetime, UTC
from google.cloud import firestore

# Servicios a monitorear y sus endpoints
SERVICES = {
    "natacha-api": "http://localhost:8080/health",
    "natacha-core": "http://localhost:8081/health",
    "natacha-health-monitor": "http://localhost:8090/health",
}

db = firestore.Client()

def check_service(name, url):
    try:
        start = time.time()
        r = requests.get(url, timeout=3)
        latency = round((time.time() - start) * 1000)
        if r.status_code == 200:
            status = "✅ Online"
        elif r.status_code >= 500:
            status = "❌ Error interno"
        else:
            status = f"⚠️ Código {r.status_code}"
    except requests.exceptions.Timeout:
        latency = None
        status = "⚠️ Timeout"
    except requests.exceptions.ConnectionError:
        latency = None
        status = "❌ No responde"
    except Exception as e:
        latency = None
        status = f"⚠️ {type(e).__name__}"

    # Guardar en Firestore
    db.collection("system_health").add({
        "service": name,
        "status": status,
        "latency_ms": latency,
        "timestamp": datetime.now(UTC).isoformat(),
    })

    print(f" - {name} → {status} ({latency or '–'} ms)")
    return status, latency

def main():
    print("🔍 Verificando estado de servicios...\n")
    for name, url in SERVICES.items():
        check_service(name, url)
        time.sleep(0.5)
    print("\n✅ Verificación completada.")

if __name__ == "__main__":
    main()
