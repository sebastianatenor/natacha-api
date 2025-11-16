from fastapi import APIRouter, Response
from datetime import datetime, timedelta
import random, json

router = APIRouter(prefix="/ops", tags=["Affective Timeline"])

# Memoria simulada de estados afectivos (últimos 5)
AFFECTIVE_MEMORY = []

def generate_timeline():
    global AFFECTIVE_MEMORY
    now = datetime.utcnow()
    moods = ["positivo", "neutral", "reflexivo", "creativo", "agotado", "ansioso"]

    # Añadir un nuevo estado simulado al timeline
    new_state = {
        "time": now.isoformat(),
        "mood": random.choice(moods),
        "energy": round(random.uniform(0.4, 0.9), 2)
    }
    AFFECTIVE_MEMORY.append(new_state)

    # Mantener solo los últimos 5
    if len(AFFECTIVE_MEMORY) > 5:
        AFFECTIVE_MEMORY = AFFECTIVE_MEMORY[-5:]

    return AFFECTIVE_MEMORY


@router.get("/affective-timeline")
def affective_timeline():
    timeline = generate_timeline()

    # Generar SVG dinámico
    svg_points = ""
    x = 60
    for state in timeline:
        y = int(180 - (state["energy"] * 100))
        svg_points += f"<circle cx='{x}' cy='{y}' r='4' fill='#61dafb'/>"
        svg_points += f"<text x='{x}' y='{y - 10}' text-anchor='middle' fill='white' font-size='9'>{state['mood']}</text>"
        x += 70

    svg = f"""
    <svg width='420' height='200' xmlns='http://www.w3.org/2000/svg'>
      <rect width='420' height='200' fill='#20232a'/>
      <text x='210' y='25' text-anchor='middle' fill='#61dafb' font-size='15'>
        🕓 Timeline Afectivo Adaptativo
      </text>
      {svg_points}
      <polyline points='60,180 130,180 200,180 270,180 340,180' stroke='#444' stroke-width='1' fill='none'/>
      <text x='210' y='190' text-anchor='middle' fill='#aaa' font-size='10'>
        {datetime.utcnow().isoformat()} UTC
      </text>
    </svg>
    """

    return Response(
        content=json.dumps({
            "status": "ok",
            "timeline": timeline,
            "svg_preview": svg
        }, ensure_ascii=False, indent=2),
        media_type="application/json"
    )
