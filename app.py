import os
from fastapi import FastAPI

from routes.memory_routes import router as memory_router, v1_router as memory_v1_router
from routes.health_route import router as health_router
from routes import memory_routes

# v1 (tasks, etc.)
from routes.v1_routes import router as v1_router

# Opcional: ops / ops_routes
ops = None
try:
    from routes import ops as ops  # ops.py estándar
except Exception:
    try:
        from routes import ops_routes as ops  # alternativa común
    except Exception:
        ops = None

# === Config de servers para OpenAPI ===
# Para simplificar, hoy fijamos el server principal a la URL de producción.
# Más adelante lo podemos parametrizar con una env var (OPENAPI_SERVER_URL).
DEFAULT_SERVER_URL = "https://natacha-api-422255208682.us-central1.run.app"
OPENAPI_SERVER_URL = os.getenv("OPENAPI_SERVER_URL", DEFAULT_SERVER_URL)

SERVERS = [{"url": OPENAPI_SERVER_URL}] if OPENAPI_SERVER_URL else []

app = FastAPI(
    title="Natacha API",
    version="1.0.0",
    servers=SERVERS or None,
)

# ===== Routers base =====

# v1 de memoria (/v1/memory/...)
app.include_router(memory_v1_router, prefix="/v1")

# health básico
app.include_router(health_router)

# memoria “legacy”
app.include_router(memory_routes.router)

# ops si existe
if ops and hasattr(ops, "router"):
    app.include_router(ops.router)


@app.get("/health")
def health():
    return {"status": "ok", "message": "Natacha API base funcionando correctamente 🚀"}


@app.get("/live")
def live():
    return {"ok": True}


@app.get("/ready")
def ready():
    # acá podrías chequear dependencia mínima (p.ej. variable obligatoria)
    return {"ok": True}


@app.get("/meta")
def meta():
    return {
        "ok": True,
        "revision": os.getenv("K_REVISION"),
        "service": os.getenv("K_SERVICE"),
        "configuration": os.getenv("K_CONFIGURATION"),
        "port": os.getenv("PORT"),
    }


# Router v1 completo (tasks v1, etc.)
app.include_router(v1_router)
