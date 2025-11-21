import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import json
from pathlib import Path

from routes import (
    memory_routes,
    health_route,
    v1_routes,
)

# === Carga automática de memoria desde Google Cloud Storage ===
import subprocess

def load_memory_from_gcs():
    """Carga memory_store.jsonl desde GCS si está en entorno Cloud Run."""
    gcs_path = "gs://natacha-memory-store/memory_store.jsonl"
    local_path = "/app/memory_store.jsonl"

    # Detectar si estamos en Cloud Run
    in_cloud_run = os.getenv("K_SERVICE") is not None

    if in_cloud_run:
        print("[BOOT] Cloud Run environment detected. Attempting to sync memory from GCS...")
        try:
            subprocess.run(
                ["gsutil", "cp", gcs_path, local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"[OK] Memory loaded from {gcs_path}")
        except Exception as e:
            print(f"[WARN] Could not load memory from GCS: {e}")
    else:
        print("[BOOT] Local environment detected. Skipping GCS memory sync.")

# Ejecutar sincronización al arranque
load_memory_from_gcs()

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

# --- ✅ Core Bridge (nuevo) ---
safe_include("routes.core_bridge")
safe_include("ops.extensions.core_bridge_ext")

# --- ✅ Affective Training (nuevo módulo adaptativo) ---
safe_include("ops.affective_train")

# --- ✅ Memory v2 Engine (long-term store) ---
safe_include("routes.memory_v2")

# --- ✅ Code Introspection Engine (v19.2) ---
safe_include("ops.introspection.code_scan")
safe_include("ops.introspection.history_reader")
safe_include("ops.introspection.self_reflect")
safe_include("ops.introspection.meta_reflect")

# --- ✅ Cognitive Evolution Engine (v19.3) ---
safe_include("ops.cognitive_evolution")

# --- ✅ Self Diagnostics Module ---
safe_include("ops.self_diagnostics")

# --- ✅ Firestore Adapter Bridge ---
safe_include("ops.firestore_adapter")

# memory v1 explícito (si existe)
try:
    from app.api_v1.memory_v1_routes import router as memory_v1_router
    app.include_router(memory_v1_router)
except Exception:
    pass

# ================================================================
# ENDPOINT OPENAPI PÚBLICO PARA CHATGPT
# ================================================================

@app.get("/openapi_public.json", include_in_schema=False)
def openapi_public():
    """
    Devuelve la especificación pública reducida para ChatGPT Actions.
    """
    base_dir = Path(__file__).parent
    path = base_dir / "public_openapi.json"

    if not path.exists():
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Natacha Public API (missing file)",
                "version": "1.0.0",
                "description": "public_openapi.json no encontrado en el contenedor."
            },
            "paths": {}
        }

    with path.open() as f:
        return json.load(f)

# ================================================================
# CUSTOM OPENAPI (INTERNO)
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=getattr(app, "title", "Natacha API"),
        version="1.0.0",
        description="Natacha API – runtime schema",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"}
    ]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
