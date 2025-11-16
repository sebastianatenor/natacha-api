import random
from datetime import datetime

def train_predictive_model(user_state=None):
    """
    Simula un entrenamiento de proyección afectiva adaptativa.
    Devuelve un dict con predicción y nivel de confianza.
    """
    moods = ["positivo", "neutral", "reflexivo", "creativo", "agotado", "ansioso"]
    mood = random.choice(moods)
    energy = round(random.uniform(0.3, 0.9), 2)
    confidence = round(random.uniform(0.5, 0.95), 2)

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "predicted_mood": mood,
        "predicted_energy": energy,
        "confidence": confidence,
        "model_version": "v1.0-sim"
    }
