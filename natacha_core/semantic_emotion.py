"""
🧭 semantic_emotion.py
Analiza texto y devuelve una interpretación emocional básica.
Incluye compatibilidad con detect_emotion() para módulos previos.
"""

import re

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
