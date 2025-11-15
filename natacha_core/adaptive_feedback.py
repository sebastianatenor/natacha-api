"""
🔁 adaptive_feedback.py
Módulo de refuerzo adaptativo: aprende sesgos afectivos y ajusta ponderaciones.
"""

import json
import os
import datetime

BIAS_FILE = "adaptive_bias.json"

def load_bias():
    if os.path.exists(BIAS_FILE):
        with open(BIAS_FILE, "r") as f:
            return json.load(f)
    return {"clarity_weight": 0.5, "energy_weight": 0.5}

def update_bias(clarity, coherence, emotion_state):
    bias = load_bias()
    clarity_w = bias["clarity_weight"]
    energy_w = bias["energy_weight"]

    # Ajuste dinámico
    clarity_w = (clarity_w + clarity) / 2
    energy_w = (energy_w + emotion_state.get("energy", 0.5)) / 2

    new_bias = {
        "clarity_weight": round(clarity_w, 3),
        "energy_weight": round(energy_w, 3),
        "last_update": datetime.datetime.utcnow().isoformat(),
        "last_emotion": emotion_state.get("mood", "neutral"),
    }

    with open(BIAS_FILE, "w") as f:
        json.dump(new_bias, f, indent=2)

    return new_bias
