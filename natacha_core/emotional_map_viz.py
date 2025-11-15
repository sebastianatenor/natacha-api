"""
🎨 emotional_map_viz.py
Convierte el mapa emocional (JSON) en una visualización SVG dinámica.
Cada punto representa una emoción reciente con color y tamaño dependiente
de confianza y energía.
"""

import json
import os
from datetime import datetime

MAP_FILE = "data/emotional_map.json"
SVG_FILE = "data/emotional_map.svg"

COLORS = {
    "neutral": "#cccccc",
    "tensa": "#ff6666",
    "serena": "#66ccff",
    "entusiasta": "#ffcc33",
    "reflexiva": "#a366ff",
}

def _scale(val, in_min, in_max, out_min, out_max):
    """Escala un valor al rango SVG."""
    return out_min + (float(val - in_min) / float(in_max - in_min)) * (out_max - out_min)

def generate_svg(limit=50, width=600, height=400):
    """Genera un SVG del mapa emocional y lo guarda en disco."""
    if not os.path.exists(MAP_FILE):
        return {"status": "no_data"}

    with open(MAP_FILE, "r") as f:
        try:
            data = json.load(f)[-limit:]
        except Exception:
            return {"status": "invalid_json"}

    svg_points = []
    for p in data:
        x = _scale(p["confidence"], 0, 1, 50, width - 50)
        y = height - _scale(p["energy"], 0, 1, 50, height - 50)
        color = COLORS.get(p.get("mood", "neutral"), "#999999")
        svg_points.append(
            f'<circle cx="{x}" cy="{y}" r="6" fill="{color}" opacity="0.8">'
            f'<title>{p["timestamp"]} | {p["mood"]} | conf={p["confidence"]}, eng={p["energy"]}</title></circle>'
        )

    svg_content = f"""<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="#1e1e1e" />
  <text x="50%" y="30" text-anchor="middle" fill="#ffffff" font-size="16">Mapa Emocional Natacha 🧠</text>
  <g>
    {' '.join(svg_points)}
  </g>
  <text x="50" y="{height - 10}" fill="#ffffff" font-size="12">Confianza →</text>
  <text x="10" y="200" fill="#ffffff" font-size="12" transform="rotate(-90,10,200)">Energía ↑</text>
  <text x="{width - 200}" y="{height - 10}" fill="#888" font-size="10">{datetime.utcnow().isoformat()}</text>
</svg>"""

    os.makedirs(os.path.dirname(SVG_FILE), exist_ok=True)
    with open(SVG_FILE, "w") as f:
        f.write(svg_content)

    return {"status": "ok", "file": SVG_FILE, "points": len(svg_points)}
