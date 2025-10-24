# ============================================
# Natacha API — Controlador General de Servicios
# ============================================
# Autor: Álvaro Sebastián
# Proyecto: Natacha AI Infra
# Descripción:
#   Servicio Flask que integra monitoreo de salud entre módulos.
#   Llama a los endpoints /ops/health de cada microservicio y notifica por WhatsApp solo ante fallas.
# ============================================

from flask import Flask, jsonify, request
from datetime import datetime
import os
import requests

app = Flask(__name__)

# --------------------------------------------------
# Variables de entorno
# --------------------------------------------------
WHATSAPP_URL = os.getenv("WHATSAPP_URL")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
DESTINO_ALERTAS = os.getenv("ADMIN_WHATSAPP", "543874120859")
SERVICE_NAME = os.getenv("SERVICE_NAME", "natacha-api")

# URLs a monitorear
SERVICIOS = {
    "natacha-core": "https://natacha-core-422255208682.us-central1.run.app/ops/health",
    "natacha-memory-console": "https://natacha-memory-console-422255208682.us-central1.run.app/ops/health",
    "natacha-api": "https://natacha-api-422255208682.us-central1.run.app/ops/health"
}

# --------------------------------------------------
# Endpoint raíz
# --------------------------------------------------
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": SERVICE_NAME,
        "message": "Natacha API en línea 🚀",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }), 200


# --------------------------------------------------
# Endpoint de salud simple
# --------------------------------------------------
@app.route("/ops/health", methods=["GET"])
def ops_health():
    return jsonify({
        "status": "ok",
        "service": SERVICE_NAME,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }), 200


# --------------------------------------------------
# Módulo central de Smart Health
# --------------------------------------------------
@app.route("/ops/smart_health", methods=["POST"])
def smart_health():
    headers = request.headers
    token = headers.get("X-Auth-Token")
    if token != "token-ultra-seguro-12345":
        return jsonify({"status": "unauthorized"}), 401

    results = {}
    global_status = "ok"

    for nombre, url in SERVICIOS.items():
        try:
            r = requests.get(url, timeout=4)
            if r.status_code == 200 and r.json().get("status") == "ok":
                results[nombre] = "ok"
            else:
                results[nombre] = f"fail ({r.status_code})"
                global_status = "alert"
        except Exception as e:
            results[nombre] = "unreachable"
            global_status = "alert"

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Si hay alerta, enviar mensaje
    if global_status != "ok":
        enviar_alerta(results, timestamp)

    return jsonify({
        "status": global_status,
        "services": results,
        "timestamp": timestamp
    }), 200


# --------------------------------------------------
# Función auxiliar: envío de alerta por WhatsApp
# --------------------------------------------------
def enviar_alerta(results, timestamp):
    if not WHATSAPP_URL or not WHATSAPP_TOKEN:
        print("⚠️ No hay credenciales de WhatsApp configuradas.")
        return

    mensaje = f"🚨 *ALERTA Natacha Smart Health*\n\n"
    mensaje += "Se detectaron fallas en los servicios:\n"
    for svc, estado in results.items():
        if estado != "ok":
            mensaje += f"• {svc}: {estado}\n"
    mensaje += f"\n⏱ {timestamp}"

    try:
        resp = requests.post(
            WHATSAPP_URL,
            headers={
                "Authorization": f"Bearer {WHATSAPP_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "messaging_product": "whatsapp",
                "to": DESTINO_ALERTAS,
                "type": "text",
                "text": {"body": mensaje}
            }
        )
        print("✅ Alerta enviada:", resp.status_code, resp.text)
    except Exception as e:
        print("❌ Error al enviar alerta:", str(e))


# --------------------------------------------------
# Ejecutor local
# --------------------------------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
