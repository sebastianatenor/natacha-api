import os
import json
import subprocess
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# ================================================================
# 1) BOOT SEQUENCE – Memory Sync
# ================================================================

def load_memory_from_gcs():
    """
    Sincroniza memory_store.jsonl desde GCS SOLO en Cloud Run.
    En local no hace nada.
    """
    gcs_path = "gs://natacha-memory-store/memory_store.jsonl"
    local_path = "/app/memory_store.jsonl"

    in_cloud_run = os.getenv("K_SERVICE") is not None

    if in_cloud_run:
        print("[BOOT] Cloud Run environment detected. Syncing memory...")
        try:
            subprocess.run(
                ["gsutil", "cp", gcs_path, local_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"[OK] Memory synced from {gcs_path}")
        except Exception as e:
            print(f"[WARN] Memory sync failed: {e}")
    else:
        print("[BOOT] Local environment: skipping memory sync.")


# Ejecutar sincronización inicial
load_memory_from_gcs()


# ================================================================
# 2) Inicialización de FastAPI
# ================================================================

app = FastAPI(
    title="Natacha API",
    version="20.0-unified-engine",
    description="Natacha – API central con motores afectivo, cognitivo y contexto unificado."
)


# ================================================================
# 3) CORS
# ================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


# ================================================================
# 4) Función segura para incluir módulos
# ================================================================

def safe_include(module_name: str):
    """
    Importa dinámicamente un módulo y si tiene un router, lo monta.
    Evita errores y deja logs claros.
    """
    try:
        module = __import__(module_name, fromlist=["router"])
        router = getattr(module, "router", None)

        if router is not None:
            app.include_router(router)
            print(f"[OK] Included: {module_name}")
        else:
            print(f"[WARN] No router found in {module_name}")

    except Exception as e:
        print(f"[SKIP] {module_name} – {e}")


# ================================================================
# 5) Routers principales
# ================================================================

from routes import memory_routes, health_route, v1_routes

app.include_router(memory_routes.router)
app.include_router(memory_routes.v1_router)
app.include_router(health_route.router)
app.include_router(v1_routes.router)


# ================================================================
# 6) Módulos opcionales (auto-loading)
# ================================================================

# Extensiones nuevas
safe_include("ops.extensions.core_bridge_ext")

# Motores afectivo y cognitivo
safe_include("ops.affective_train")
safe_include("ops.cognitive_evolution")

# Motores unificados de contexto
safe_include("unified_core.context_engine")
safe_include("unified_core.snapshot_engine")

# Introspección
safe_include("ops.introspection.code_scan")
safe_include("ops.introspection.history_reader")
safe_include("ops.introspection.self_reflect")
safe_include("ops.introspection.meta_reflect")

# Diagnóstico
safe_include("ops.self_diagnostics")
safe_include("ops.firestore_adapter")

# Router público para context_bundle
safe_include("routes.context_unified")


# ================================================================
# 7) Memory v1 (si existe)
# ================================================================

try:
    from app.api_v1.memory_v1_routes import router as memory_v1_router
    app.include_router(memory_v1_router)
    print("[OK] Included legacy memory v1 routes")
except Exception:
    print("[INFO] No legacy memory v1 routes available.")


# ================================================================
# 8) Root endpoint
# ================================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "natacha-unified-v20",
        "message": "Natacha API – fully operational 🚀"
    }


# ================================================================
# 9) OpenAPI PÚBLICO para ChatGPT
# ================================================================

@app.get("/openapi_public.json", include_in_schema=False)
def openapi_public():
    """
    Devuelve openapi público reducido para ChatGPT Actions.
    """
    path = Path(__file__).parent / "public_openapi.json"

    if not path.exists():
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Natacha Public API (MISSING FILE)",
                "version": "1.0.0",
                "description": "public_openapi.json no encontrado."
            },
            "paths": {}
        }

    with path.open() as f:
        return json.load(f)


# ================================================================
# 10) Custom OpenAPI interno
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="20.0",
        description="Esquema interno unificado de Natacha",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"},
        {"url": "http://localhost:8080"},
    ]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
