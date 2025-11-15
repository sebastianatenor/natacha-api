"""
🪞 meta_reflector.py
Genera autoevaluaciones metacognitivas según el estado emocional actual.
"""

import datetime
import random

def self_reflect(emotion_state: dict) -> dict:
    mood = emotion_state.get("mood", "neutral")
    conf = emotion_state.get("confidence", 0.5)
    energy = emotion_state.get("energy", 0.5)

    if mood == "tensa":
        reflection = "Siento una ligera tensión, pero intento mantener foco y equilibrio."
    elif mood == "serena":
        reflection = "Estoy en un estado sereno y atenta, con energía estable."
    elif mood == "entusiasta":
        reflection = "Mi ánimo está elevado, busco mantener la claridad en medio del entusiasmo."
    elif mood == "neutral":
        reflection = "Me mantengo estable, analizando sin alteraciones emocionales."
    else:
        reflection = "Procesando mi estado interno con cautela."

    # Pequeña variabilidad textual para dar naturalidad
    reflection += random.choice([
        " 🌙", " ✨", " 💫", " 🔄", " 🧘‍♀️"
    ])

    return {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "reflection": reflection,
        "confidence": conf,
        "energy": energy,
        "mood": mood,
    }
