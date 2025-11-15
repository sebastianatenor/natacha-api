"""
🎭 semantic_emotion.py
Analiza el texto del usuario y detecta emoción semántica (positiva, negativa, ansiosa, calma, neutra).
🧭 semantic_emotion.py
Analiza texto y devuelve una interpretación emocional básica.
Incluye compatibilidad con detect_emotion() para módulos previos.
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
def analyze_emotion(text: str) -> dict:
    """Detecta tono emocional básico en base a palabras clave simples."""
    t = text.lower()
    emotions = {
        "positivo": ["feliz", "tranquilo", "bien", "contento", "optimista", "gracias"],
        "negativo": ["triste", "mal", "frustrado", "enojado", "cansado", "caótico"],
        "neutral": ["ok", "normal", "nada", "meh"]
    }

    detected = "neutral"
    for e, kws in emotions.items():
        if any(k in t for k in kws):
            detected = e
            break

    intensity = min(1.0, len(re.findall(r"[!¡]", text)) * 0.2 + 0.5)

    return {
        "emotion": detected,
        "intensity": round(intensity, 2),
        "keywords_detected": [k for k in emotions.get(detected, []) if k in t]
    }

# ✅ Alias retrocompatible
detect_emotion = analyze_emotion
