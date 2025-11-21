# ============================================================
# LEGACY RUNTIME – NO USAR COMO ENTRYPOINT EN CLOUND RUN
# Runtime oficial de Natacha API: service_main:app
# Este módulo se mantiene solo para compatibilidad y debugging puntual.
# ============================================================

import os
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

# === Config de servers para OpenAPI ===
# Para simplificar, hoy fijamos el server principal a la URL de producción.
# Más adelante lo podemos parametrizar con una env var (OPENAPI_SERVER_URL).
DEFAULT_SERVER_URL = "https://natacha-api-422255208682.us-central1.run.app"
OPENAPI_SERVER_URL = os.getenv("OPENAPI_SERVER_URL", DEFAULT_SERVER_URL)

SERVERS = [{"url": OPENAPI_SERVER_URL}] if OPENAPI_SERVER_URL else []

# === Inicialización de la app principal ===
app = FastAPI(
    title="Natacha Core",
    version="18.0-affective-projection",
    description="Core API con proyección cognitivo-afectiva, timeline y sincronización adaptativa.",
    servers=SERVERS,
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
