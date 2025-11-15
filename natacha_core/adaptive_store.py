"""
💾 adaptive_store.py
Persistencia local para las métricas adaptativas del sistema de razonamiento.
Guarda y carga las estadísticas en un archivo JSON, para que sobrevivan a reinicios del Core.
"""

import json
import os
import datetime

STATE_FILE = "adaptive_state.json"

def save_state(metrics: dict):
    """Guarda el estado actual de métricas en disco."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(metrics, f, indent=2)
        return {"status": "saved", "file": STATE_FILE, "timestamp": datetime.datetime.utcnow().isoformat()}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def load_state():
    """Carga el estado de métricas desde disco, si existe."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}
