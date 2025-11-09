from fastapi import FastAPI
from routes.health_route import router as health_router

from routes import memory_routes, ops  # 👈 Asegurate de incluir memory_routes

app = FastAPI()
app.include_router(health_router)

# Registrar los routers
app.include_router(ops.router)
app.include_router(memory_routes.router)  # 👈 Muy importante


@app.get("/health")
def health():
    return {"status": "ok", "message": "Natacha API base funcionando correctamente 🚀"}
