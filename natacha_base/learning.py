import datetime

from flask import Blueprint, jsonify

learning_bp = Blueprint("learning", __name__)


@learning_bp.route("/ops/learning_report", methods=["GET"])
def learning_report():
    """Devuelve el estado del sistema de aprendizaje de Natacha"""
    report = {
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "insights": {
            "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "error_count": 0,
            "warning_count": 0,
            "hypotheses": ["Sin errores repetidos detectados recientemente."],
        },
        "lessons": [{"info": "Sin lecciones registradas aún."}],
    }
    return jsonify(report), 200
