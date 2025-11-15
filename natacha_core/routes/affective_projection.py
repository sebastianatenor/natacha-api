from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import json, os, random
from adaptive_trainer import train_predictive_model

router = APIRouter(prefix="/ops", tags=["affective"])

def load_affective_state():
    state_file = "/app/adaptive_state.json"
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mood": "neutral", "energy": 0.5, "intensity": 0.5}

def predict_future_states(current):
    """Proyecta el estado afectivo para 5 min, 30 min y 2 h."""
    energy = current.get("energy", 0.5)
    intensity = current.get("intensity", 0.5)
    base_mood = current.get("mood", "neutral")

    deltas = [0.05, -0.03, 0.1]
    moods = ["positivo", "neutral", "reflexivo", "tenso"]
    predictions = []

    for i, delta in enumerate(deltas):
        factor = random.uniform(-0.05, 0.05)
        energy_proj = max(0.0, min(1.0, energy + delta + factor))
        mood_proj = (
            base_mood
            if abs(delta) < 0.04
            else random.choice([m for m in moods if m != base_mood])
        )
        t_future = datetime.utcnow() + [timedelta(minutes=5), timedelta(minutes=30), timedelta(hours=2)][i]
        predictions.append(
            {
                "time": t_future.isoformat(),
                "mood": mood_proj,
                "energy": round(energy_proj, 2),
            }
        )

    return predictions

@router.get("/affective-projection")
def affective_projection():
    """Predicción cognitivo-afectiva basada en estado adaptativo."""
    current = load_affective_state()

    try:
        model_pred = train_predictive_model(current)
    except Exception:
        model_pred = {"trend": "stable", "confidence": 0.6}

    future = predict_future_states(current)

    svg_points = []
    for idx, p in enumerate(future):
        x = 80 + idx * 120
        y = int(180 - p["energy"] * 100)
        svg_points.append(f"<circle cx='{x}' cy='{y}' r='5' fill='#61dafb'/>")
        svg_points.append(
            f"<text x='{x}' y='{y - 10}' text-anchor='middle' fill='white' font-size='10'>{p['mood']}</text>"
        )

    svg = f"""
    <svg width='420' height='200' xmlns='http://www.w3.org/2000/svg'>
      <rect width='420' height='200' fill='#20232a'/>
      <text x='210' y='25' text-anchor='middle' fill='#61dafb' font-size='15'>
        🔮 Proyección Cognitivo-Afectiva
      </text>
      {''.join(svg_points)}
      <text x='210' y='190' text-anchor='middle' fill='#aaa' font-size='10'>
        Último estado: {current.get('mood', 'N/A')} | Energía actual: {current.get('energy', 0.5):.2f}
      </text>
    </svg>
    """

    return JSONResponse(
        content={
            "status": "ok",
            "current": current,
            "future_projection": future,
            "model": model_pred,
            "svg_preview": svg,
        }
    )
