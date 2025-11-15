from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import json, os, random

try:
    from affective_regulator import regulate_state
except ImportError:
    regulate_state = None

router = APIRouter(prefix="/ops", tags=["affective"])

def load_adaptive_state():
    state_file = "/app/adaptive_state.json"
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"mood": "neutral", "confidence": 0.5, "energy": 0.5, "intensity": 0.5}

@router.get("/affective-map")
def affective_map():
    """Visualización afectiva dinámica completa."""
    current = load_adaptive_state()

    # Intentar proyectar con regulador adaptativo
    projected = None
    if regulate_state:
        try:
            projected = regulate_state(current, "(sistema)")
        except TypeError:
            projected = regulate_state(current)
        except Exception:
            projected = None

    if not projected:
        projected = {
            "mood": random.choice(["positivo", "neutral", "reflexivo", "tenso"]),
            "energy": round(random.uniform(0.2, 0.9), 2),
            "intensity": round(random.uniform(0.3, 1.0), 2)
        }

    # 🎨 Códigos de color por estado
    mood_colors = {
        "positivo": "#4caf50",   # verde
        "neutral": "#61dafb",    # azul
        "reflexivo": "#9c27b0",  # violeta
        "tenso": "#f44336"       # rojo
    }
    color = mood_colors.get(projected.get("mood"), "#61dafb")

    energy = projected.get("energy", 0.5)
    intensity = projected.get("intensity", 0.5)
    energy_width = int(energy * 300)
    bg_opacity = 0.3 + intensity * 0.6

    svg = f"""
    <svg width='420' height='200' xmlns='http://www.w3.org/2000/svg'>
      <rect width='420' height='200' fill='{color}' fill-opacity='{bg_opacity}'/>
      <rect x='60' y='150' width='{energy_width}' height='10' fill='{color}' rx='4'/>
      <rect x='60' y='150' width='300' height='10' fill='none' stroke='#444' stroke-width='1' rx='4'/>
      <text x='210' y='40' text-anchor='middle' fill='white' font-size='16'>🧠 Mapa Afectivo</text>
      <text x='210' y='90' text-anchor='middle' fill='white' font-size='13'>
        Estado: {projected.get("mood", "N/A").upper()}
      </text>
      <text x='210' y='110' text-anchor='middle' fill='white' font-size='12'>
        Energía: {energy:.2f} | Intensidad: {intensity:.2f}
      </text>
      <text x='210' y='180' text-anchor='middle' fill='#ddd' font-size='10'>
        {datetime.utcnow().isoformat()} UTC
      </text>
    </svg>
    """

    return JSONResponse(
        content={
            "status": "ok",
            "current": current,
            "prediction": projected,
            "svg_preview": svg
        }
    )
