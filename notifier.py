from datetime import datetime

import requests
from google.cloud import firestore

db = firestore.Client()
WHATSAPP_ENDPOINT = "https://natacha-api-505068916737.us-central1.run.app/whatsapp"


def send_alert(message):
    print(f"📩 Enviando alerta: {message}")
    db.collection("notifications").add(
        {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "channel": "WhatsApp",
        }
    )
    try:
        requests.post(
            WHATSAPP_ENDPOINT, json={"numero": "54911XXXXXXXX", "mensaje": message}
        )
    except Exception as e:
        print(f"⚠️ Error al enviar mensaje: {e}")


if __name__ == "__main__":
    send_alert("⚠️ Alerta de prueba — sistema en modo autónomo.")
