import os
import threading
import time
from datetime import datetime

import requests

INTERVAL_MINUTES = int(
    os.getenv("AUTO_CHECK_INTERVAL", "15")
)  # cada 15 minutos por defecto
HEALTH_URL = os.getenv(
    "NATACHA_HEALTH_URL",
    "https://natacha-health-monitor-422255208682.us-central1.run.app",
)


def auto_infra_check_loop():
    """Bucle que ejecuta diagnósticos automáticos cada X minutos."""
    while True:
        try:
            print(
                f"🕒 Ejecutando chequeo automático: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            r = requests.post(f"{HEALTH_URL}/run_auto_infra_check", timeout=20)
            if r.status_code == 200:
                print("✅ Diagnóstico automático ejecutado correctamente.")
            else:
                print(f"⚠️ Error al ejecutar diagnóstico automático: {r.status_code}")
        except Exception as e:
            print("🚨 Error en auto_scheduler:", str(e))
        time.sleep(INTERVAL_MINUTES * 60)


def start_scheduler():
    """Inicia el hilo de ejecución automática."""
    thread = threading.Thread(target=auto_infra_check_loop, daemon=True)
    thread.start()
    print(f"🧠 AutoScheduler iniciado — cada {INTERVAL_MINUTES} minutos.")
