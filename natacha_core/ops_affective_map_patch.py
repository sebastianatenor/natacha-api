from affective_regulator import load_timeline, predict_future_state
from fastapi import Response
import json

def patched_affective_map():
    """Devuelve proyección afectiva con SVG incrustado correctamente escapado."""
    timeline = load_timeline()
    prediction = predict_future_state(timeline)

    svg = f'''
    <svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
      <rect width="400" height="200" fill="#20232a"/>
      <text x="200" y="40" text-anchor="middle" fill="#61dafb" font-size="16">Mapa Afectivo - Proyección</text>
      <text x="200" y="100" text-anchor="middle" fill="white" font-size="14">
        Estado Previsto: {prediction["predicted_mood"].upper()}
      </text>
      <text x="200" y="130" text-anchor="middle" fill="#61dafb" font-size="12">
        Energía proyectada: {prediction["predicted_energy"]}
      </text>
    </svg>
    '''

    result = {
        "status": "ok",
        "prediction": prediction,
        "svg_preview": svg
    }

    # Devolvemos respuesta JSON explícita
    return Response(
        content=json.dumps(result, ensure_ascii=False, indent=2),
        media_type="application/json"
    )
