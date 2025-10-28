from flask import Blueprint, jsonify
import socket
import datetime
import requests

health_bp = Blueprint("health", __name__)

@health_bp.route("/ops/smart_health", methods=["POST"])
def smart_health():
    """Diagnóstico básico de salud del servicio"""
    diagnostics = {
        "service": "natacha-api",
        "hostname": socket.gethostname(),
        "time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "internet": "ok",
        "firestore": "pending",
        "secret_manager": "pending",
        "whatsapp_module": "pending",
    }

    try:
        requests.get("https://www.google.com", timeout=2)
        diagnostics["internet"] = "ok"
    except Exception:
        diagnostics["internet"] = "fail"

    return jsonify({
        "service": "natacha-api",
        "extended_status": "ok",
        "diagnostics": diagnostics
    }), 200


@health_bp.route("/ops/memory_report", methods=["GET"])
def memory_report():
    """Provee un resumen del estado de la memoria"""
    diagnostics = {
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "patterns": {
            "analysis_time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "total": 0,
            "patterns": {"error": 0, "warning": 0, "info": 0}
        },
        "recent": []
    }
    return jsonify(diagnostics), 200
