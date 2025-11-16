# natacha_core/adaptive_trainer.py

from datetime import datetime
from .affective_predictor import train_predictive_model

def run_adaptive_cycle():
    """
    Ejecuta un ciclo completo de aprendizaje adaptativo.
    Integra la predicción afectiva con ajustes internos simulados.
    """
    result = train_predictive_model()

    # Simular un ajuste interno (por ejemplo, ajustar sesgo adaptativo)
    bias_shift = round(result["confidence"] * 0.05, 3)
    new_state = {
        "timestamp": datetime.utcnow().isoformat(),
        "applied_bias_shift": bias_shift,
        "predicted_mood": result["predicted_mood"],
        "energy_level": result["predicted_energy"],
        "model_version": result["model_version"]
    }

    return {
        "status": "ok",
        "message": "Ciclo adaptativo completado",
        "details": new_state
    }
