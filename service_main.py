import os
import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# === Routers principales ===
from routes import (
    memory_routes,
    health_route,
    v1_routes,
    natacha_routes,
    actions_openapi,
    memory_engine_routes,  # motor de contexto /memory/engine/*
)
from routes.tasks_routes import router as tasks_router
from routes.people_routes import router as people_router
from routes.project_routes import router as project_router
from routes.ops_routes import router as ops_routes
from routes.semantic_v2_routes import router as semantic_v2_router
from routes.natacha_healthcheck import router as natacha_healthcheck_router  # ⬅️ NUEVO
from routes.calendar_routes import router as calendar_router

# === Carga automática de memoria desde Google Cloud Storage ===
import subprocess


def load_memory_from_gcs():
    """Carga memory_store.jsonl desde GCS si está en entorno Cloud Run."""
    gcs_path = "gs://natacha-memory-store/memory_store.jsonl"
    local_path = "/app/memory_store.jsonl"

    in_cloud_run = os.getenv("K_SERVICE") is not None

    if in_cloud_run:
        print("[BOOT] Cloud Run environment detected. Attempting to sync memory from GCS...")
        try:
            subprocess.run(
                ["gsutil", "cp", gcs_path, local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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
    description="API central de Natacha con motor afectivo adaptativo.",
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
app.include_router(memory_routes.router)         # /memory/add, /memory/search
app.include_router(memory_routes.v1_router)      # /memory/engine/* v1, etc.
app.include_router(memory_engine_routes.router)  # /memory/engine/context_bundle
app.include_router(health_route.router)          # /health, /meta
app.include_router(v1_routes.router)             # /v1/memory/*
app.include_router(tasks_router)                 # /tasks/add, /tasks/list, /tasks/update
app.include_router(people_router)
app.include_router(project_router)
app.include_router(ops_routes)                   # /ops/*
app.include_router(actions_openapi.router)       # /actions/openapi.json
app.include_router(natacha_routes.router)        # /natacha/respond
app.include_router(semantic_v2_router)           # /memory/v2/semantic/*
app.include_router(natacha_healthcheck_router)   # ⬅️ NUEVO: /natacha/healthcheck
app.include_router(calendar_router)

# --- Módulos opcionales ---
safe_include("routes.core_bridge")
safe_include("ops.extensions.core_bridge_ext")
safe_include("ops.affective_train")
safe_include("routes.memory_v2")
safe_include("ops.introspection.code_scan")
safe_include("ops.introspection.history_reader")
safe_include("ops.introspection.self_reflect")
safe_include("ops.introspection.meta_reflect")
safe_include("ops.cognitive_evolution")
safe_include("ops.self_diagnostics")
safe_include("ops.firestore_adapter")


print("[BOOT] Listando rutas registradas en FastAPI:")
for r in app.routes:
    try:
        methods = getattr(r, "methods", None)
        print("[ROUTE]", getattr(r, "path", None), methods)
    except Exception as e:
        print("[ROUTE_ERR]", r, e)

# memory v1 explícito (si existe)
try:
    from app.api_v1.memory_v1_routes import router as memory_v1_router

    app.include_router(memory_v1_router)
except Exception:
    pass


# ================================================================
# DEBUG: listar rutas registradas en tiempo de ejecución
# ================================================================
from fastapi.routing import APIRoute  # type: ignore


@app.get("/debug/routes", include_in_schema=False)
def debug_routes():
    """
    Devuelve las rutas registradas en esta instancia de FastAPI.
    Sirve para comparar local vs Cloud Run.
    """
    rutas = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            rutas.append({
                "path": route.path,
                "methods": sorted(list(route.methods)),
            })
    return rutas


# ================================================================
# OPENAPI PÚBLICO PARA CHATGPT
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
                "description": "public_openapi.json no encontrado en el contenedor.",
            },
            "paths": {},
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


# === Endpoint raíz ===
@app.get("/")
def root():
    return {
        "status": "ok",
        "version": "19.0",
        "message": "Natacha API – núcleo afectivo adaptativo 🚀",
    }
