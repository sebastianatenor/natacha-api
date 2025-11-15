import datetime
import json
import requests
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from memory_bridge import store_memory, retrieve_context
from context_reasoner import generate_response
from cognitive_evaluator import evaluate_context_quality
from adaptive_reasoner import apply_adaptive_style, determine_mode
from adaptive_trainer import update_metrics, get_stats
from adaptive_store import load_state

app = FastAPI(
    title="Natacha Core Service",
    description="Servicio central de procesamiento cognitivo de Natacha 🧠",
    version="1.0.0",
)


# === MODELOS ===
class ProcessInput(BaseModel):
    text: str
    user: str | None = None
    metadata: dict | None = None


# === ENDPOINTS BASE ===
@app.get("/health")
def health():
    return {
        "status": "ok",
        "message": "Core local funcionando correctamente 🚀",
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


@app.post("/respond_with_evaluation")
def respond_with_evaluation(payload: ProcessInput):
    """
    Extiende /respond_with_context con evaluación cognitiva,
    emoción semántica, autorregulación afectiva y refuerzo adaptativo.
    """
    from cognitive_evaluator import evaluate_context_quality
    from context_reasoner import generate_response
    from adaptive_trainer import update_metrics, get_stats
    from adaptive_reasoner import apply_adaptive_style, determine_mode
    from semantic_emotion import detect_emotion
    from affective_regulator import regulate_state
    from adaptive_feedback import update_bias
    from adaptive_store import load_state, save_state

    text = payload.text

    # 1️⃣ Obtener contexto
    context_data = retrieve_context()
    context_items = context_data.get("context", []) if isinstance(context_data, dict) else []

    # 2️⃣ Generar razonamiento base
    reasoning_result = generate_response(text, context_items)

    # 3️⃣ Evaluar claridad/coherencia
    eval_result = evaluate_context_quality(context_items)
    adaptive_stats = update_metrics(eval_result)

    # 4️⃣ Detectar emoción semántica del texto
    user_emotion = detect_emotion(text)

    # 5️⃣ Autorregular estado afectivo
    current_state = {
        "confidence": adaptive_stats.get("stats", {}).get("avg_clarity", 0.5),
        "energy": adaptive_stats.get("stats", {}).get("avg_coherence", 0.5)
    }
    new_emotion_state = regulate_state(current_state, text)

    # 6️⃣ Aprendizaje de sesgos afectivos
    bias_data = update_bias(
        eval_result.get("clarity_score", 0.5),
        eval_result.get("coherence_score", 0.5),
        new_emotion_state
    )

    # 7️⃣ Guardar memoria adaptativa y respuesta estilizada
    save_state(adaptive_stats)
    final_response = apply_adaptive_style(reasoning_result["response"])

    return {
        "status": "ok",
        "timestamp": reasoning_result["timestamp"],
        "response": final_response,
        "evaluation": eval_result,
        "user_emotion": user_emotion,
        "regulated_state": new_emotion_state,
        "adaptive_stats": adaptive_stats,
        "adaptive_bias": bias_data
    }


# === ENDPOINT /respond_with_evaluation ===
@app.post("/respond_with_evaluation")
def respond_with_evaluation(payload: ProcessInput):
    """
    Analiza el texto, evalúa coherencia y claridad, actualiza métricas adaptativas,
    aplica el tono cognitivo actual y devuelve respuesta razonada con estilo adaptativo.
    """
    text = payload.text

    context_data = retrieve_context()
    context_items = context_data.get("context", []) if isinstance(context_data, dict) else []

    reasoning_result = generate_response(text, context_items)
    eval_result = evaluate_context_quality(context_items)

    memory_result = store_memory(payload.user or "anon", text)
    adaptive_stats = update_metrics(eval_result)

    # 🧠 Fase 7: aplicar autoexpresión adaptativa al texto final
    reasoning_result["response"] = apply_adaptive_style(reasoning_result["response"])

    return {
        "status": "ok",
        "timestamp": reasoning_result["timestamp"],
        "response": reasoning_result["response"],
        "context_summary": reasoning_result["context_summary"],
        "evaluation": eval_result,
        "memory_result": memory_result,
        "adaptive_stats": adaptive_stats,
    }


# === OPS ENDPOINTS ===
@app.get("/ops/adaptive-stats")
def ops_adaptive_stats():
    """Devuelve métricas actuales del sistema adaptativo."""
    return get_stats()


@app.get("/ops/adaptive-mode")
def ops_adaptive_mode():
    """Devuelve el modo adaptativo y tono actual de Natacha."""
    metrics = load_state() or {"avg_clarity": 0.0, "avg_coherence": 0.0}
    mode = determine_mode()
    return {
        "status": "ok",
        "mode": mode,
        "metrics": metrics,
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

# ============================================================
# 💫 Fase 15+: Inteligencia afectiva y metacognitiva
# ============================================================
from emotional_map import get_map
from emotional_memory import get_emotional_history, load_emotion_state
from adaptive_reasoner import reflect_and_map

@app.get("/ops/emotional-map")
def ops_emotional_map():
    """Devuelve la trayectoria emocional reciente (confianza/energía)."""
    return {
        "status": "ok",
        "map": get_map(50)
    }

@app.get("/ops/affective-history")
def ops_affective_history():
    """Devuelve los últimos estados emocionales registrados."""
    return {
        "status": "ok",
        "history": get_emotional_history(15)
    }

@app.get("/ops/self-reflection")
def ops_self_reflection():
    """Devuelve una autoevaluación metacognitiva instantánea."""
    emotion = load_emotion_state() or {"mood": "neutral", "confidence": 0.5, "energy": 0.5}
    reflection = reflect_and_map(emotion)
    return {
        "status": "ok",
        "reflection": reflection
    }

# ============================================================
# 🎨 Visualización emocional (SVG)
# ============================================================
from fastapi.responses import FileResponse
from emotional_map_viz import generate_svg, SVG_FILE

@app.get("/ops/emotional-map/svg")
def ops_emotional_map_svg():
    """Genera y devuelve un SVG del mapa emocional."""
    result = generate_svg()
    if result.get("status") == "ok":
        return FileResponse(SVG_FILE, media_type="image/svg+xml")
    return result
