import datetime, json
from semantic_emotion import analyze_emotion
from affective_regulator import regulate_state

def reflect_on_self(user_emotion, system_state):
    """Analiza empatía y consistencia emocional."""
    empathy = 1.0 - abs(user_emotion.get("intensity", 0) - system_state.get("energy", 0))
    alignment = "alta" if empathy > 0.7 else "moderada" if empathy > 0.4 else "baja"

    reflection = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "user_emotion": user_emotion.get("emotion"),
        "system_mood": system_state.get("mood"),
        "alignment": alignment,
        "empathic_alignment": round(empathy, 3)
    }

    # Actualizar estado regulado
    regulated = regulate_state(user_emotion)
    reflection["regulated_state"] = regulated
    return reflection
