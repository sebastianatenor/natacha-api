"""
⚖️ affective_regulator.py
Autorregulación afectiva: ajusta energía y confianza según emoción detectada.
"""

import datetime
from semantic_emotion import detect_emotion

def regulate_state(current_state: dict, user_text: str) -> dict:
    """Ajusta el estado afectivo interno en función del texto y el estado previo."""
    emotion_data = detect_emotion(user_text)
    emotion = emotion_data["emotion"]
    intensity = emotion_data["intensity"]

    confidence = current_state.get("confidence", 0.5)
    energy = current_state.get("energy", 0.5)

    if emotion == "positivo":
        confidence = min(1.0, confidence + 0.2 * intensity)
        energy = min(1.0, energy + 0.1 * intensity)
    elif emotion == "negativo":
        confidence = max(0.1, confidence - 0.2 * intensity)
        energy = max(0.1, energy - 0.15 * intensity)
    elif emotion == "ansioso":
        confidence = max(0.2, confidence - 0.1)
        energy = min(1.0, energy + 0.2)
    elif emotion == "calmo":
        confidence = min(1.0, confidence + 0.1)
        energy = max(0.2, energy - 0.1)

    return {
        "mood": emotion,
        "confidence": round(confidence, 3),
        "energy": round(energy, 3),
        "intensity": intensity,
        "last_update": datetime.datetime.utcnow().isoformat(),
        "last_user_emotion": emotion,
    }
