import os
import json
import threading
from pathlib import Path

print("[BOOT] service_main loaded — before FastAPI init")

# ================================================================
# FAST BOOT FLAG (CRÍTICO PARA CLOUD RUN)
# ================================================================
os.environ.setdefault("NATACHA_FAST_BOOT", "1")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# ================================================================
# 1) BOOT SEQUENCE – Memory Sync (CLOUD RUN SAFE)
# ================================================================

def load_memory_from_gcs():
    """
    Sincroniza memory_store.jsonl desde GCS SOLO en Cloud Run.
    Corre en background, nunca bloquea el arranque.
    IMPORTANTE: resetea el MemoryIndex al finalizar.
    """
    try:
        in_cloud_run = os.getenv("K_SERVICE") is not None
        local_path = "/tmp/memory_store.jsonl"

        if not in_cloud_run:
            print("[BOOT] Local environment: skipping memory sync.")
            return

        if Path(local_path).exists():
            print("[BOOT] Memory already present, skipping GCS sync.")
            return

        print("[BOOT] Cloud Run detected. Starting async memory sync…")

        from google.cloud import storage

        client = storage.Client()
        bucket = client.bucket("natacha-memory-store")
        blob = bucket.blob("memory_store.jsonl")
        blob.download_to_filename(local_path)

        print("[OK] Memory synced from GCS")

        # 🔥 CLAVE: resetear el singleton para que se reconstruya el índice
        from unified_core.memory_lazy import reset_memory_index
        reset_memory_index()
        print("[MEMORY] Memory index reset after GCS sync")

    except Exception as e:
        print(f"[WARN] Memory sync skipped: {e}")


def start_background(fn):
    t = threading.Thread(target=fn, daemon=True)
    t.start()


# ================================================================
# 2) FASTAPI INIT (ULTRA RÁPIDO)
# ================================================================

app = FastAPI(
    title="Natacha API",
    version="20.4-fast-boot",
    description="Natacha – Cloud Run safe fast boot"
)

# --------------------------------------------------
# LIVENESS / ALIVE PROBE (Cloud Run friendly)
# --------------------------------------------------

@app.get("/__alive", tags=["system"])
async def alive():
    return {
        "status": "alive",
        "service": "natacha-api",
        "engine": "natacha-unified",
    }

# ================================================================
# 3) STARTUP HOOK (NO BLOQUEANTE)
# ================================================================

@app.on_event("startup")
def on_startup():
    # Memory sync siempre en background
    start_background(load_memory_from_gcs)

    # Post-startup SOLO en background
    try:
        from ops.startup.post_startup import launch_post_startup
        start_background(launch_post_startup)
        print("[STARTUP] post_startup launched in background")
    except Exception as e:
        print(f"[STARTUP][SKIP] post_startup unavailable: {e}")

    print("[STARTUP] Fast boot startup completed")

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
# 5) SAFE INCLUDE
# ================================================================

def safe_include(module_name: str):
    try:
        module = __import__(module_name, fromlist=["router"])
        router = getattr(module, "router", None)

        if router:
            app.include_router(router)
            print(f"[OK] Included: {module_name}")
        else:
            print(f"[WARN] No router found in {module_name}")

    except Exception as e:
        print(f"[SKIP] {module_name} – {e}")

# ================================================================
# 6) RUTAS BASE (SIEMPRE ACTIVAS)
# ================================================================

from routes import health_route
from routes.context_unified import router as context_unified_router
from routes.memory_unified import router as memory_unified_router

app.include_router(health_route.router)
app.include_router(memory_unified_router)
app.include_router(context_unified_router)

# ================================================================
# 7) MÓDULOS OPCIONALES (DIFERIDOS)
# ================================================================

if os.getenv("NATACHA_FAST_BOOT") != "1":
    safe_include("ops.extensions.core_bridge_ext")
    safe_include("ops.affective_train")
    safe_include("ops.cognitive_evolution")

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

    safe_include("ops.memory.post_rollback")
    safe_include("ops.agent.interact")
else:
    print("[BOOT] FAST BOOT active — optional modules deferred")

print("[INFO] Legacy memory routes DISABLED (A2 clean)")

# ================================================================
# 8) ROOT
# ================================================================

@app.get("/")
def root():
    return {
        "status": "ok",
        "engine": "natacha-unified-v20.4-fast-boot",
        "message": "Natacha API – Cloud Run FAST BOOT ready 🚀"
    }

# ================================================================
# 9) OPENAPI PUBLIC
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
# 10) OPENAPI INTERNO
# ================================================================

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="Natacha Internal API",
        version="20.4",
        description="Natacha internal API (fast boot)",
        routes=app.routes,
    )

    schema["servers"] = [
        {"url": "https://natacha-api-422255208682.us-central1.run.app"},
        {"url": "http://localhost:8080"},
    ]

    app.openapi_schema = schema
    return schema

app.openapi = custom_openapi
