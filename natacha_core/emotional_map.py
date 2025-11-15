"""
🌈 emotional_map.py
Genera y actualiza un mapa emocional continuo a partir de las coordenadas
(confianza, energía). Sirve para visualización o análisis temporal.
"""

import json
import os
import datetime

MAP_FILE = "data/emotional_map.json"

def _ensure_dir():
    os.makedirs(os.path.dirname(MAP_FILE), exist_ok=True)

def add_point(confidence: float, energy: float, mood: str):
    _ensure_dir()
    point = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "confidence": round(confidence, 3),
        "energy": round(energy, 3),
        "mood": mood
    }
    data = []
    if os.path.exists(MAP_FILE):
        with open(MAP_FILE, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append(point)
    with open(MAP_FILE, "w") as f:
        json.dump(data[-100:], f, indent=2)  # mantener últimos 100 puntos
    return point

def get_map(limit=50):
    if not os.path.exists(MAP_FILE):
        return []
    try:
        with open(MAP_FILE, "r") as f:
            data = json.load(f)
            return data[-limit:]
    except Exception as e:
        return [{"error": str(e)}]
