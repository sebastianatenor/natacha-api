import os
import json
import threading
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# ================================================================
# 1) BOOT SEQUENCE – Memory Sync (Cloud Run SAFE)
# ================================================================

def load_memory_from_gcs():
    """
    Sincroniza memory_store.jsonl desde GCS SOLO en Cloud Run.
    Se ejecuta en background, nunca bloquea el arranque.
    """
    in_cloud_run = os.getenv("K_SERVICE") is not None

    if not in_cloud_run:
        print("[BOOT] Local environment: skipping memory sync.")
        return

    print("[BOOT] Cloud Run detected. Starting async memory sync…")

    try:
        from google.cloud import storage

        bucket_name = "natacha-memory-store"
        blob_name = "memory_store.jsonl"
        local_path = "/tmp/memory_store.jsonl"

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)

        blob.download_to_filename(local_path)
        print(f"[OK] Memory synced from gs://{bucket_name}/{blob_name}")

    except Exception as e:
        print(f"[WARN] Memory sync skipped: {e}")


def start_memory_sync_background():
    t = threading.Thread(
        target=load_memory_from_gcs,
        daemon=True
    )
    t.start()


# ================================================================
# 2) Inicialización FastAPI
# ================================================================

app = FastAPI(
    title="Natacha API",
    version="20.2-clean-memory",
    description="Natacha – API central con memoria lazy unificada (Cloud Run safe)."
)

# ================================================================
# 3) STARTUP HOOK (ÚNICO punto válido en Cloud Run)
# ================================================================

@app.on_event("startup")
def on_startup():
    # ===============================
    # 1) Async memory sync from GCS
    # ===============================
    start_memory_sync_background()

    # ===============================
    # 2) Lazy memory ensure (SAFE)
    # ===============================
    try:
        from unified_core.memory_lazy import get_memory_engine
        mem = get_memory_engine()
        mem.ensure_loaded()
        print("[STARTUP] Memory engine ensured")
    except Exception as e:
        print(f"[STARTUP][MEMORY][SKIP] {e}")

    # ===============================
    # 3) Auto-warmup semantic core
    # ===============================
    try:
        from ops.startup.auto_warmup import maybe_auto_warmup
        maybe_auto_warmup()
        print("[STARTUP] Auto-warmup evaluated")
    except Exception as e:
        print(f"[STARTUP][AUTO-WARMUP][ERROR] {e}")

# ================================================================
# 4) CORS
# ================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ================================================================
# 5) Safe include helper
# ================================================================

def safe_include(module_name: str):
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
# 6) Routers PRINCIPALES (UNIFICADOS)
# ================================================================

from routes import health_route
from routes.context_unified import router as context_unified_router
from routes.memory_unified import router as memory_unified_router

app.include_router(health_route.router)
app.include_router(memory_unified_router)
app.include_router(context_unified_router)

# ================================================================
# 7) Módulos opcionales / introspección
# ================================================================

safe_include("ops.extensions.core_bridge_ext")
safe_include("ops.affective_train")
safe_include("ops.cognitive_evolution")

safe_include("unified_core.snapshot_engine")

safe_include("ops.introspection.code_scan")
safe_include("ops.introspection.history_reader")
safe_include("ops.introspection.self_reflect")
safe_include("ops.introspection.meta_reflect")

safe_include("ops.self_diagnostics")
safe_include("ops.firestore_adapter")

safe_include("routes.benchmark")
safe_include("routes.system_state")
safe_include("routes.system_decide")
safe_include("routes.system_diagnose")
safe_include("routes.warmup")
safe_include("routes.memory_rollback")
safe_include("routes.memory_snapshot")
safe_include("routes.memory_snapshots")

# ❌ IMPORTANTE: NO se incluye memory_engine_alias
print("[INFO] Legacy memory routes DISABLED (A2 clean)")

# ================================================================
# 8) Root
# ================================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "natacha-unified-v20.2",
        "message": "Natacha API – Clean memory / Cloud Run ready 🚀"
    }

# ================================================================
# 9) OpenAPI público
# ================================================================

@app.get("/openapi_public.json", include_in_schema=False)
def openapi_public():
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
# 10) OpenAPI interno
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="20.2",
        description="Esquema interno unificado de Natacha (clean memory)",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"},
        {"url": "http://localhost:8080"},
    ]

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi
