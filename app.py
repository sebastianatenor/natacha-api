from fastapi import FastAPI

from routes.memory_routes import router as memory_router, v1_router as memory_v1_router
from routes.health_route import router as health_router
from routes.v1_routes import router as v1_router

# Intentar importar rutas afectivas si existen
ops = None
try:
    from routes import affective_map
    from routes import affective_projection
except Exception:
    ops = None

# === Inicialización de la app principal ===
app = FastAPI(
    title="Natacha Core",
    version="18.0-affective-projection",
    description="Core API con proyección cognitivo-afectiva, timeline y sincronización adaptativa."
)

# Routers principales
app.include_router(memory_router)
app.include_router(memory_v1_router)
app.include_router(health_router)
app.include_router(v1_router)

if ops:
    app.include_router(affective_map.router)
    app.include_router(affective_projection.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Natacha Core activo 🚀"}
