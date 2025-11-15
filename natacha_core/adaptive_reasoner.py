import datetime
from adaptive_store import load_state
from emotional_memory import save_emotion_state, load_emotion_state

# === Estado emocional persistente ===
_emotional_state = load_emotion_state() or {
    "mood": "neutral",
    "confidence": 0.5,
    "energy": 0.5,
    "last_update": datetime.datetime.utcnow().isoformat()
}

_POSITIVE_WORDS = [
    "gracias", "feliz", "claro", "genial", "excelente", "me gusta", "bien", "contento", "armonía", "tranquilo", "inspirado"
]
_NEGATIVE_WORDS = [
    "triste", "mal", "confuso", "enojado", "estresado", "difícil", "frustrado", "complicado", "no entiendo", "cansado"
]


def _detect_user_emotion(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in _POSITIVE_WORDS):
        return "positive"
    elif any(w in text_lower for w in _NEGATIVE_WORDS):
        return "negative"
    return "neutral"


def _apply_emotional_decay():
    """Reduce gradualmente energía y ajusta confianza con el paso del tiempo."""
    global _emotional_state
    now = datetime.datetime.utcnow()

    try:
        last_update = datetime.datetime.fromisoformat(_emotional_state["last_update"])
    except Exception:
        last_update = now

    elapsed_minutes = (now - last_update).total_seconds() / 60.0
    if elapsed_minutes < 1:
        return _emotional_state

    decay_factor = min(0.05 * elapsed_minutes, 0.3)
    energy = max(0.0, _emotional_state["energy"] - decay_factor)
    confidence = min(1.0, _emotional_state["confidence"] + decay_factor / 2)

    if elapsed_minutes > 10:
        new_mood = "serena" if confidence > 0.6 else "neutral"
    else:
        new_mood = _emotional_state["mood"]

    _emotional_state.update({
        "mood": new_mood,
        "confidence": round(confidence, 3),
        "energy": round(energy, 3),
        "last_update": now.isoformat(),
    })
    save_emotion_state(_emotional_state)
    return _emotional_state


def _stability_factor(clarity, coherence):
    avg = (clarity + coherence) / 2
    variance = abs(clarity - coherence)
    stability = max(0.0, min(1.0, 1 - variance - (0.5 - avg) ** 2))
    return round(stability, 3)


def _update_emotional_state(clarity, coherence, user_emotion="neutral"):
    global _emotional_state
    _apply_emotional_decay()

    avg = (clarity + coherence) / 2
    prev_conf = _emotional_state["confidence"]
    prev_energy = _emotional_state["energy"]

    base_conf = 0.7 * prev_conf + 0.3 * avg
    base_energy = 0.7 * prev_energy + 0.3 * (1 - avg)

    if user_emotion == "positive":
        base_conf = min(1.0, base_conf + 0.1)
        base_energy = max(0.2, base_energy - 0.1)
        mood = "serena" if base_conf > 0.7 else "entusiasta"
    elif user_emotion == "negative":
        base_conf = max(0.0, base_conf - 0.15)
        base_energy = min(1.0, base_energy + 0.15)
        mood = "tensa"
    else:
        mood = _emotional_state["mood"]

    _emotional_state.update({
        "mood": mood,
        "confidence": round(base_conf, 3),
        "energy": round(base_energy, 3),
        "last_update": datetime.datetime.utcnow().isoformat(),
        "last_user_emotion": user_emotion,
    })

    save_emotion_state(_emotional_state)
    return _emotional_state


def _microstate_label(mode, mood, confidence, energy):
    """Genera microestados combinados usando un continuo afectivo."""
    if mood == "tensa":
        return "tensa pero reflexiva ⚡" if mode == "focused" else "tensa pero analítica ⚡"
    if mood == "serena":
        return "serenamente enfocada 🌙" if mode == "focused" else "serenamente creativa 🌙"
    if mood == "entusiasta":
        return "creativamente equilibrada 🌞" if mode == "creative" else "entusiasta pero clara 🌞"
    if mood == "neutral":
        return "neutral y analítica ✨" if mode == "focused" else "naturalmente equilibrada ✨"
    return f"{mood} ({confidence:.2f}/{energy:.2f})"


def determine_mode(user_text: str = ""):
    state = load_state() or {}
    clarity = state.get("avg_clarity", 0.0)
    coherence = state.get("avg_coherence", 0.0)
    stability = _stability_factor(clarity, coherence)
    user_emotion = _detect_user_emotion(user_text)
    emotion = _update_emotional_state(clarity, coherence, user_emotion)

    if clarity < 0.3 and coherence < 0.3:
        mode = "focused"
        tone = "analítico y conciso"
    elif clarity >= 0.5 and coherence >= 0.5:
        mode = "creative"
        tone = "expresivo y poético"
    else:
        mode = "balanced"
        tone = "fluido y natural"

    microstate = _microstate_label(mode, emotion["mood"], emotion["confidence"], emotion["energy"])

    return {
        "mode": mode,
        "tone": tone,
        "clarity": round(clarity, 3),
        "coherence": round(coherence, 3),
        "stability": stability,
        "microstate": microstate,
        "emotion": emotion,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def apply_adaptive_style(response_text: str, user_text: str = "") -> str:
    mode_info = determine_mode(user_text)
    tone = mode_info["tone"]
    microstate = mode_info["microstate"]
    confidence = mode_info["emotion"]["confidence"]
    energy = mode_info["emotion"]["energy"]

    user_emotion = mode_info["emotion"].get("last_user_emotion", "neutral")
    empathy_note = {
        "positive": "Siento tu energía positiva y la acompaño con serenidad 🌿",
        "negative": "Percibo tu tensión y mantengo calma para equilibrar ⚖️",
        "neutral": "Me mantengo en sintonía tranquila contigo 🌙",
    }[user_emotion]

    return (
        f"[Modo {mode_info['mode'].upper()} - Microestado: {microstate}] "
        f"{response_text.strip()} ({tone}). {empathy_note} "
        f"Confianza {confidence:.2f}, energía {energy:.2f}."
    )

# === Extensión Fase 15+: Mapa emocional + metacognición ===
from meta_reflector import self_reflect
from emotional_map import add_point

def reflect_and_map(emotion_state: dict):
    """Actualiza el mapa emocional y genera autoevaluación."""
    reflection = self_reflect(emotion_state)
    add_point(
        confidence=emotion_state["confidence"],
        energy=emotion_state["energy"],
        mood=emotion_state["mood"]
    )
    return reflection
