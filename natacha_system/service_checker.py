import time
from datetime import datetime

import requests
from google.cloud import firestore

# Inicialización Firestore
db = firestore.Client()
COLLECTION_NAME = "system_health"

# Servicios a monitorear
SERVICES = {
    "natacha-api": "http://natacha-api:8080/health",
    "natacha-core": "http://natacha-core:8080/health",
    "natacha-health-monitor": "http://natacha-health-monitor:8080/health",
}

CHECK_INTERVAL = 60  # segundos


def log_status_to_firestore(service_name, status, response_time_ms):
    """Registra el estado del servicio en Firestore."""
    entry = {
        "service": service_name,
        "status": status,
        "response_time_ms": response_time_ms,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    try:
        db.collection(COLLECTION_NAME).add(entry)
        print(f"📡 Registro enviado a Firestore: {service_name} → {status}")
    except Exception as e:
        print(f"⚠️ Error al escribir en Firestore: {e}")


def check_service(name, url):
    """Verifica si un servicio está activo."""
    try:
        start = time.time()
        r = requests.get(url, timeout=5)
        elapsed_ms = round((time.time() - start) * 1000)
        if r.status_code == 200:
            print(f"✅ {name} → Online ({elapsed_ms} ms)")
            log_status_to_firestore(name, "online", elapsed_ms)
        else:
            print(f"❌ {name} → Error HTTP {r.status_code}")
            log_status_to_firestore(name, f"http_{r.status_code}", elapsed_ms)
    except Exception as e:
        print(f"❌ {name} → No responde ({e})")
        log_status_to_firestore(name, "offline", None)


def main():
    print("🔍 Iniciando monitoreo dinámico de servicios Natacha...\n")
    while True:
        for service, url in SERVICES.items():
            check_service(service, url)
        print(f"\n⏱️ Próxima verificación en {CHECK_INTERVAL} segundos...\n")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
