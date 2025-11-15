"""
🌩 adaptive_store.py
Persistencia híbrida: local + sincronización con GCS (Google Cloud Storage).
Mantiene coherencia entre nodos y respaldo del estado cognitivo adaptativo.
💾 adaptive_store.py
Persistencia local para las métricas adaptativas del sistema de razonamiento.
Guarda y carga las estadísticas en un archivo JSON, para que sobrevivan a reinicios del Core.
"""

import json
import os
import datetime
import subprocess

STATE_FILE = "adaptive_state.json"
GCS_BUCKET = "gs://natacha-memory-store/adaptive_state.json"

def save_state(metrics: dict):
    """Guarda localmente y sincroniza con GCS si gsutil está disponible."""
    try:
        # Guardar local
        with open(STATE_FILE, "w") as f:
            json.dump(metrics, f, indent=2)
        timestamp = datetime.datetime.utcnow().isoformat()

        # Sincronizar con GCS (si gsutil está instalado)
        try:
            subprocess.run(
                ["gsutil", "cp", STATE_FILE, GCS_BUCKET],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return {"status": "saved+synced", "file": STATE_FILE, "timestamp": timestamp}
        except Exception as e:
            return {"status": "saved_local_only", "detail": str(e), "timestamp": timestamp}


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
    """Carga desde GCS si está disponible, sino desde local."""
    # Intentar primero desde GCS
    try:
        subprocess.run(
            ["gsutil", "cp", GCS_BUCKET, STATE_FILE],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except Exception:
        pass  # si falla, seguimos con el archivo local

    """Carga el estado de métricas desde disco, si existe."""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        return {"error": str(e)}
