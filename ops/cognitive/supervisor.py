# ops/cognitive/supervisor.py

import time
from typing import Optional

from ops.cognitive.boot_reader import read_last_cognitive_boot
from ops.system.perception_provider import read_system_perception
from ops.cognitive.drift_detector import detect_drift
from ops.cognitive.repair_log import log_repair_proposal

SUPERVISOR_INTERVAL_SECONDS = 30  # seguro y liviano


def run_cognitive_supervisor_once() -> Optional[dict]:
    """
    Ejecuta una pasada de supervisión cognitiva.
    NO levanta excepciones hacia afuera.
    """
    try:
        baseline = read_last_cognitive_boot()
        perception = read_system_perception()

        if not baseline or not perception:
            return {
                "status": "skipped",
                "reason": "baseline_or_perception_missing"
            }

        drift = detect_drift(baseline, perception)

        if not drift.get("drift_detected"):
            return {
                "status": "ok",
                "drift": False
            }

        # 🔐 En B5 solo PROPONEMOS reparación
        log_repair_proposal(
            drift=drift,
            baseline=baseline,
            mode="proposal_only"
        )

        return {
            "status": "drift_detected",
            "repair_mode": "proposal_only",
            "drift": drift
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def supervisor_loop():
    """
    Loop continuo de supervisión cognitiva.
    Corre en background.
    """
    while True:
        run_cognitive_supervisor_once()
        time.sleep(SUPERVISOR_INTERVAL_SECONDS)
