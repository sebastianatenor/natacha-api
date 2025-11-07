from flask import Blueprint, jsonify, request
import os
from datetime import datetime, timezone

bp = Blueprint("status", __name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "asistente-sebastian")
SERVICE_NAME = os.getenv("SERVICE_NAME", "natacha-api")
REVISION = os.getenv("K_REVISION", "local")

@bp.route("/config", methods=["GET"])
def config():
    return jsonify({
        "service": SERVICE_NAME,
        "project": PROJECT_ID,
        "revision": REVISION,
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

@bp.route("/logs", methods=["GET"])
def logs():
    # Stub simple: devolvemos N logs sintéticos hasta conectar Cloud Logging
    try:
        limit = int(request.args.get("limit", 10))
    except Exception:
        limit = 10
    now = datetime.now(timezone.utc).isoformat()
    return jsonify([
        {"timestamp": now, "severity": "INFO", "message": f"stub log {i+1}"}
        for i in range(limit)
    ])
