import os
import time

import requests


class Comms:
    """Maneja comunicaciones de Natacha (WhatsApp, logs, etc.)."""

    def __init__(self):
        self.token = os.getenv("META_WHATSAPP_TOKEN")
        self.phone_id = "785334911339043"  # ID de tu número de negocio (confirmado)
        self.numero_default = "543874120859"

    def send_whatsapp(self, numero: str, mensaje: str):
        """Envía un mensaje de WhatsApp usando la API oficial de Meta."""
        if not self.token:
            print("❌ Token de WhatsApp no configurado (META_WHATSAPP_TOKEN).")
            return

        url = f"https://graph.facebook.com/v23.0/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": numero or self.numero_default,
            "type": "text",
            "text": {"body": mensaje},
        }

        for intento in range(3):
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=10)
                if resp.status_code == 200:
                    print(f"✅ WhatsApp enviado correctamente a {numero}")
                    return
                else:
                    print(
                        f"⚠️ Error WhatsApp intento {intento+1}: {resp.status_code} — {resp.text}"
                    )
            except Exception as e:
                print(f"❌ Excepción WhatsApp: {e}")
            time.sleep(2)
        print("🚨 Fallo tras 3 intentos de enviar WhatsApp.")
