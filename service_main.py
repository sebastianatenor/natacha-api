import os
import json
import threading
import time
from pathlib import Path

print("[BOOT] service_main loaded — before FastAPI init")

# ================================================================
# FAST BOOT FLAG (CRÍTICO PARA CLOUD RUN)
# ================================================================
os.environ.setdefault("NATACHA_FAST_BOOT", os.getenv("NATACHA_FAST_BOOT", "1"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# ================================================================
# Helpers
# ================================================================

def start_background(fn):
    t = threading.Thread(target=fn, daemon=True)
    t.start()


def _safe_reset_memory_index(reason: str = ""):
    """
    Resetea el singleton del MemoryIndex para forzar rebuild.
    Nunca debe romper el arranque.
    """
    try:
        from unified_core.memory_lazy import reset_memory_index
        reset_memory_index()
        if reason:
            print(f"[MEMORY] Memory index reset ({reason})")
        else:
            print("[MEMORY] Memory index reset")
    except Exception as e:
        print(f"[MEMORY][WARN] Could not reset memory index: {e}")


# ================================================================
# 1) BOOT SEQUENCE – Memory Sync (CLOUD RUN SAFE)
# ================================================================

def load_memory_from_gcs():
    """
    Sincroniza memory_store.jsonl desde GCS SOLO en Cloud Run.
    Corre en background, nunca bloquea el arranque.

    IMPORTANTE:
    - Si el archivo YA existe en /tmp, igual resetea MemoryIndex
      (porque puede haber quedado cacheado en NullMemoryIndex por una llamada temprana).
    """
    try:
        in_cloud_run = os.getenv("K_SERVICE") is not None
        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        p = Path(local_path)

        if not in_cloud_run:
            print("[BOOT] Local environment: skipping memory sync.")
            return

        # Si el archivo ya existe, NO descargar de nuevo (fast), pero SÍ resetear el índice
        if p.exists():
            print("[BOOT] Memory already present, skipping GCS sync.")
            _safe_reset_memory_index("memory already present on boot")
            return

        print("[BOOT] Cloud Run detected. Starting async memory sync…")

        from google.cloud import storage

        client = storage.Client()
        bucket_name = os.getenv("NATACHA_MEMORY_BUCKET", "natacha-memory-store")
        blob_name = os.getenv("NATACHA_MEMORY_BLOB", "memory_store.jsonl")

        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.download_to_filename(local_path)

        print("[OK] Memory synced from GCS")

        # CLAVE: resetear para que se reconstruya el índice con el archivo ya presente
        _safe_reset_memory_index("after GCS sync")

    except Exception as e:
        print(f"[WARN] Memory sync skipped: {e}")


def wait_and_reset_memory_index():
    """
    Evita la race condition:
    si /context/unified se llama ANTES de que llegue /tmp/memory_store.jsonl,
    el singleton queda cacheado vacío. Este watcher espera a que el archivo exista y tenga tamaño,
    y recién ahí resetea el índice (en background).
    """
    try:
        in_cloud_run = os.getenv("K_SERVICE") is not None
        if not in_cloud_run:
            return

        local_path = os.getenv("NATACHA_MEMORY_LOCAL", "/tmp/memory_store.jsonl")
        p = Path(local_path)

        # ventana máxima de espera (segundos) – ajustable por env var
        max_wait = int(os.getenv("NATACHA_MEMORY_WAIT_SECONDS", "30"))
        step = float(os.getenv("NATACHA_MEMORY_WAIT_STEP", "0.5"))

        waited = 0.0
        while waited < max_wait:
            try:
                if p.exists() and p.stat().st_size > 0:
                    _safe_reset_memory_index("waiter detected memory file ready")
                    return
            except Exception:
                pass
            time.sleep(step)
            waited += step

        # Si llegamos acá, no apareció (no rompemos nada)
        print(f"[MEMORY][WARN] memory_store.jsonl not ready after {max_wait}s — continuing")
    except Exception as e:
        print(f"[MEMORY][WARN] waiter failed: {e}")


# ================================================================
# 2) FASTAPI INIT (ULTRA RÁPIDO)
# ================================================================

app = FastAPI(
    title="Natacha API",
    version="20.5-fast-boot",
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

    # Watcher anti-race: resetea cuando /tmp esté listo (aunque sync llegue tarde)
    start_background(wait_and_reset_memory_index)

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
# 6.1) OS ROUTERS — EXPLICIT (PUBLIC & GPT-COMPATIBLE)
# ================================================================

try:
    from routes.system_state import router as system_state_router
    app.include_router(system_state_router)
    print("[OK] system_state router enabled")
except Exception as e:
    print(f"[SKIP] system_state router: {e}")

try:
    from routes.system_diagnose import router as system_diagnose_router
    app.include_router(system_diagnose_router)
    print("[OK] system_diagnose router enabled")
except Exception as e:
    print(f"[SKIP] system_diagnose router: {e}")

try:
    from routes.system_decide import router as system_decide_router
    app.include_router(system_decide_router)
    print("[OK] system_decide router enabled")
except Exception as e:
    print(f"[SKIP] system_decide router: {e}")

try:
    from routes.tasks_routes import router as tasks_router
    app.include_router(tasks_router)
    print("[OK] tasks router enabled")
except Exception as e:
    print(f"[SKIP] tasks router: {e}")

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
        "engine": "natacha-unified-v20.5-fast-boot",
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
        version="20.5",
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
