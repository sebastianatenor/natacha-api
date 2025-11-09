from fastapi import FastAPI
from routes.health_route import router as health_router

from routes import memory_routes
ops = None
try:
    from routes import ops as ops  # ops.py estándar
except Exception:
    try:
        from routes import ops_routes as ops  # alternativa común
    except Exception:
        ops = None  # 👈 Asegurate de incluir memory_routes

app = FastAPI()
app.include_router(health_router)

# Registrar los routers
app.include_router(ops.router)
app.include_router(memory_routes.router)  # 👈 Muy importante
if ops and hasattr(ops, 'router'):
    app.include_router(ops.router)


@app.get("/health")
def health():
    return {"status": "ok", "message": "Natacha API base funcionando correctamente 🚀"}