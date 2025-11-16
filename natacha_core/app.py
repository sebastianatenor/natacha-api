from fastapi import FastAPI
from routes import affective_map, affective_projection, affective_timeline

from memory_bridge import store_memory, retrieve_context
from context_reasoner import generate_response
from cognitive_evaluator import evaluate_context_quality
from adaptive_reasoner import apply_adaptive_style, determine_mode
from adaptive_trainer import update_metrics, get_stats
from adaptive_store import load_state

app = FastAPI(
    title="Natacha Core",
    version="19.0-affective-timeline",
    description="Core API con proyección cognitivo-afectiva, timeline emocional y mapa adaptativo."
)

# Routers principales
app.include_router(affective_map.router)
app.include_router(affective_projection.router)
app.include_router(affective_timeline.router)

@app.get("/")
def root():
    return {"status": "ok", "message": "Natacha Core activo 🚀"}
