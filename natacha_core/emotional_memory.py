"""
💫 emotional_memory.py
Registra y mantiene un historial de estados emocionales y reflexiones metacognitivas.
Guarda en formato JSONL incremental para facilitar visualizaciones y análisis.
"""

import json
import os
import datetime

MEMORY_FILE = "affective_memory.jsonl"

def save_emotion_state(state: dict):
    """Guarda el estado emocional actual en memoria local y retorna el mismo."""
    try:
        with open(MEMORY_FILE, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "state": state
            }) + "\n")
        return {"status": "saved", "file": MEMORY_FILE}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def load_emotion_state():
    """Carga el último estado emocional registrado."""
    if not os.path.exists(MEMORY_FILE):
        return None
    try:
        with open(MEMORY_FILE, "r") as f:
            lines = f.readlines()
            if not lines:
                return None
            last = json.loads(lines[-1])
            return last.get("state", {})
    except Exception as e:
        return {"error": str(e)}

def get_emotional_history(limit=10):
    """Devuelve los últimos 'limit' estados emocionales."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, "r") as f:
            lines = f.readlines()[-limit:]
            return [json.loads(line) for line in lines]
    except Exception as e:
        return [{"error": str(e)}]
