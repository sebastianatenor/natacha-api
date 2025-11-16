import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import (
    memory_routes,
    health_route,
    v1_routes,
)

# === Función segura para incluir módulos opcionales ===
def safe_include(module_name: str):
    try:
        module = __import__(module_name, fromlist=["router"])
        if hasattr(module, "router"):
            app.include_router(module.router)
            print(f"[OK] Included: {module_name}")
        else:
            print(f"[WARN] No router in {module_name}")
    except Exception as e:
        print(f"[SKIP] {module_name} – {e}")

# === Inicialización de la app principal ===
app = FastAPI(
    title="Natacha API",
    version="19.0-adaptive-affective-training",
    description="API central de Natacha con motor afectivo adaptativo."
)

# === Configuración de CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers principales ===
app.include_router(memory_routes.router)
app.include_router(memory_routes.v1_router)
app.include_router(health_route.router)
app.include_router(v1_routes.router)

# === Módulos opcionales ===
safe_include("ops.affective_train")

# === Endpoints de sistema ===
@app.get("/")
def root():
    return {
        "status": "ok",
        "version": "19.0",
        "message": "Natacha API – núcleo afectivo adaptativo 🚀"
    }
