from fastapi import FastAPI
from routes.affective_map import router as affective_router
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
    title="Natacha Core",
    version="16.1-modular",
    description="Motor afectivo modular con endpoints integrados."
)

# Registrar módulos de rutas
app.include_router(affective_router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Natacha Core operativo 🚀"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
app.include_router(affective_projection.router)
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


@app.post("/process")
def process(input_data: ProcessInput):
    """Simula procesamiento cognitivo básico"""
    text = input_data.text.lower()
    response = {}

    if "hola" in text:
        response["intent"] = "greeting"
        response["reply"] = "¡Hola! Soy Natacha Core. ¿En qué puedo ayudarte?"
    elif "estado" in text or "status" in text:
        response["intent"] = "system_status"
        response["reply"] = "Todo el ecosistema Natacha está estable y sincronizado 💾⚙️"
    else:
        response["intent"] = "unknown"
        response["reply"] = "No estoy segura de qué quisiste decir 🤔"

    try:
        payload = {
            "key": f"core_log_{datetime.datetime.utcnow().isoformat()}",
            "value": json.dumps(
                {
                    "input": input_data.text,
                    "intent": response["intent"],
                    "reply": response["reply"],
                    "user": input_data.user,
                    "metadata": input_data.metadata,
                }
            ),
        }
        requests.post(
            "http://natacha-memory-console:8080/memory/store", json=payload, timeout=3
        )
    except Exception as e:
        response["memory_sync"] = f"⚠️ Error al registrar en memoria: {e}"

    return {"core_status": "ok", "input": input_data.text, "response": response}


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
# 🧩 Integración con memoria contextual
# ============================================================

from memory_bridge import store_memory, retrieve_context

@app.post("/analyze_with_memory")
def analyze_with_memory(payload: ProcessInput):
    """
    Versión extendida de /analyze que guarda el texto en la memoria contextual
    y devuelve el contexto reciente junto al análisis.
    """
    text = payload.text

    # Obtener contexto reciente
    context_data = retrieve_context()

    # Hacer el análisis básico reutilizando la lógica anterior
    analysis = {
        "length": len(text),
        "words": len(text.split()),
        "has_question": "?" in text,
        "has_greeting": any(w.lower() in text.lower() for w in ["hola", "buenas", "hey"]),
        "timestamp": str(datetime.datetime.utcnow()),
    }

# 4️⃣ Guardar nueva memoria y actualizar métricas adaptativas
    try:
        memory_result = store_memory(payload.user or "anon", text)
        adaptive_stats = update_metrics(eval_result)
    except Exception as e:
        memory_result = {"error": str(e)}
        adaptive_stats = {"error": str(e)}

    return {
        "analysis_status": "ok",
        "text": text,
        "analysis": analysis,
        "memory_context": context_data,
        "memory_store_result": memory_result,
    }

# ===========================================================
# 🧠 Nuevo endpoint: /respond_with_context
# Usa la memoria contextual y el razonador para generar respuestas inteligentes
# ===========================================================

from context_reasoner import generate_response
from memory_bridge import retrieve_context, store_memory

@app.post("/respond_with_context")
def respond_with_context(payload: ProcessInput):
    """
    Analiza el texto del usuario, obtiene el contexto desde la memoria,
    genera una respuesta razonada y guarda la nueva entrada.
    """
    user_text = payload.text

    # Obtener contexto reciente desde el motor de memoria
    context_data = retrieve_context()
    context_items = context_data.get("context", []) if isinstance(context_data, dict) else []

    # Generar respuesta contextualizada
    result = generate_response(user_text, context_items)

    # Guardar nueva entrada en la memoria contextual
    try:
        memory_result = store_memory(payload.user or "anon", user_text)
    except Exception as e:
        memory_result = {"error": str(e)}

    return {
        "status": "ok",
        "result": result,
        "memory_result": memory_result,
        "adaptive_stats": adaptive_stats,
    }

# ============================================================
# 🧠 Extensión Fase 4: Evaluación Cognitiva Integrada
# ============================================================

from cognitive_evaluator import evaluate_context_quality
from adaptive_trainer import update_metrics, get_stats

@app.post("/respond_with_evaluation")
def respond_with_evaluation(payload: ProcessInput):
    """
    Extiende /respond_with_context para incluir una evaluación cognitiva
    de la coherencia y claridad del contexto actual.
    """
    text = payload.text

    # 1️⃣ Obtener contexto reciente desde la memoria contextual
    context_data = retrieve_context()
    context_items = context_data.get("context", []) if isinstance(context_data, dict) else []

    # 2️⃣ Generar razonamiento con el módulo contextual previo
    from context_reasoner import generate_response
    reasoning_result = generate_response(text, context_items)

    # 3️⃣ Evaluar calidad cognitiva del contexto
    eval_result = evaluate_context_quality(context_items)

    # 4️⃣ Guardar nueva memoria
    memory_result = store_memory(payload.user or "anon", text)
    adaptive_stats = update_metrics(eval_result)

    return {
        "status": "ok",
        "timestamp": reasoning_result["timestamp"],
        "response": reasoning_result["response"],
        "context_summary": reasoning_result["context_summary"],
        "evaluation": eval_result,
        "memory_result": memory_result,
        "adaptive_stats": adaptive_stats,
    }

@app.get("/ops/adaptive-stats")
def ops_adaptive_stats():
    """Devuelve las métricas actuales del sistema adaptativo."""
    return get_stats()
