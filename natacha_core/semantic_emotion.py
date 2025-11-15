"""
🎭 semantic_emotion.py
Analiza el texto del usuario y detecta emoción semántica (positiva, negativa, ansiosa, calma, neutra).
"""

import re

def detect_emotion(text: str) -> dict:
    """Detecta la emoción predominante del texto mediante análisis léxico simple."""
    text = text.lower()
    emotion = "neutral"
    intensity = 0.5

    positive = ["feliz", "bien", "contento", "genial", "claro", "tranquilo", "gracias"]
    negative = ["mal", "triste", "enojado", "confuso", "frustrante", "miedo", "ansioso"]
    calm = ["calma", "tranquilo", "sereno", "pausado"]
    anxious = ["estresado", "nervioso", "tenso", "preocupado"]

    if any(w in text for w in positive):
        emotion = "positivo"
        intensity = 0.8
    elif any(w in text for w in negative):
        emotion = "negativo"
        intensity = 0.7
    elif any(w in text for w in calm):
        emotion = "calmo"
        intensity = 0.6
    elif any(w in text for w in anxious):
        emotion = "ansioso"
        intensity = 0.7

    # Ajuste por exclamaciones o repeticiones
    if "!" in text:
        intensity = min(1.0, intensity + 0.2)

    return {
        "emotion": emotion,
        "intensity": round(intensity, 2),
        "keywords_detected": re.findall(r'\b[a-záéíóúñ]+\b', text),
    }
