from fastapi import APIRouter
import random
from datetime import datetime

router = APIRouter(prefix="/ops/affective-train", tags=["Affective Training"])

@router.post("/run")
def run_affective_training():
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
