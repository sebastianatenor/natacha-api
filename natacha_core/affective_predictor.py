import datetime, math, statistics

def predict_future_state(timeline):
    """Predice el estado emocional próximo según tendencias."""
    if not timeline:
        return {"prediction": "neutral", "confidence": 0.0}

    energies = [t.get("energy", 0) for t in timeline[-5:]]
    avg_energy = statistics.mean(energies)
    predicted_energy = min(1.0, max(0.0, avg_energy + 0.1))

    mood = "positivo" if predicted_energy > 0.6 else "neutral" if predicted_energy > 0.3 else "negativo"

    return {
        "predicted_mood": mood,
        "predicted_energy": round(predicted_energy, 2),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
