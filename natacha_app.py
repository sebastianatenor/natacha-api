import os
from fastapi import FastAPI

from routes.memory_routes import router as memory_router
from routes.tasks_routes import router as tasks_router
from routes.semantic_routes import router as semantic_router
from routes.embeddings_routes import router as embeddings_router
from routes.ops_routes import router as ops_router
from routes.core_routes import router as core_router  # 👈 NUEVO

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "message": "Natacha API base funcionando correctamente 🚀"}

# memoria
app.include_router(memory_router)

# tareas
app.include_router(tasks_router)

# semántica
app.include_router(semantic_router)

# embeddings
app.include_router(embeddings_router)

# ops
app.include_router(ops_router)

# core / dashboard
app.include_router(core_router)  # 👈 NUEVO

# === startup: cargar contexto operativo de Natacha ===
try:
    from intelligence.startup import load_operational_context

    api_base = os.getenv("NATACHA_CONTEXT_API")
    if not api_base:
        api_base = "http://127.0.0.1:8002"

    load_operational_context(api_base=api_base, limit=20)
except Exception as e:
    print(f"⚠️ Natacha startup context not loaded: {e}")
